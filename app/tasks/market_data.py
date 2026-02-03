from app.core.celery_app import celery_app
from app.api.finnhub_client import FinnhubClient
from app.api.massive_client import MassiveAPIClient
from app.core.config import Config
import redis
import json


# Initialize Redis client
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)


@celery_app.task(name='app.tasks.market_data.fetch_candles')
def fetch_candles(symbol, resolution='1', days_back=1):
    """
    Asynchronous task to fetch candle data from Finnhub
    This task does not block the main execution thread
    """
    finnhub_client = FinnhubClient()
    candles = finnhub_client.get_candles(symbol, resolution, days_back)
    
    if candles.get('status') == 'success':
        # Store in Redis with expiration
        redis_key = f"candles:{symbol}:{resolution}"
        redis_client.setex(
            redis_key,
            3600,  # Expire after 1 hour
            json.dumps(candles)
        )
        
        # Publish to Redis pub/sub for real-time updates
        redis_client.publish(
            'market_data',
            json.dumps({
                'type': 'candles',
                'symbol': symbol,
                'data': candles
            })
        )
    
    return candles


@celery_app.task(name='app.tasks.market_data.fetch_quote')
def fetch_quote(symbol):
    """
    Asynchronous task to fetch real-time quote from Finnhub
    """
    finnhub_client = FinnhubClient()
    quote = finnhub_client.get_quote(symbol)
    
    if quote.get('status') == 'success':
        # Store in Redis
        redis_key = f"quote:{symbol}"
        redis_client.setex(
            redis_key,
            60,  # Expire after 1 minute
            json.dumps(quote)
        )
        
        # Publish for real-time updates
        redis_client.publish(
            'market_data',
            json.dumps({
                'type': 'quote',
                'symbol': symbol,
                'data': quote
            })
        )
    
    return quote


@celery_app.task(name='app.tasks.market_data.fetch_sentiment')
def fetch_sentiment(symbol):
    """
    Asynchronous task to fetch sentiment data from Massive API
    """
    massive_client = MassiveAPIClient()
    sentiment = massive_client.get_market_sentiment(symbol)
    
    if sentiment.get('status') == 'success':
        # Store in Redis
        redis_key = f"sentiment:{symbol}"
        redis_client.setex(
            redis_key,
            1800,  # Expire after 30 minutes
            json.dumps(sentiment)
        )
        
        # Publish for real-time updates
        redis_client.publish(
            'market_data',
            json.dumps({
                'type': 'sentiment',
                'symbol': symbol,
                'data': sentiment
            })
        )
    
    return sentiment


@celery_app.task(name='app.tasks.market_data.fetch_all_market_data')
def fetch_all_market_data(symbols=None):
    """
    Fetch all market data for configured symbols
    This is a high-level task that coordinates multiple data fetches
    """
    if symbols is None:
        symbols = Config.DEFAULT_SYMBOLS
    
    results = {}
    for symbol in symbols:
        # Queue subtasks for parallel execution
        fetch_candles.delay(symbol)
        fetch_quote.delay(symbol)
        fetch_sentiment.delay(symbol)
        results[symbol] = 'queued'
    
    return results
