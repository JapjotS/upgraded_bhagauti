from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from app.core.config import Config
from app.core.celery_app import make_celery
from app.tasks.market_data import fetch_all_market_data, fetch_quote, fetch_candles, fetch_sentiment
from app.tasks.trading import analyze_signal
import redis
import json
import eventlet

# Monkey patch for eventlet
eventlet.monkey_patch()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SocketIO with Redis message queue
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    message_queue=Config.SOCKETIO_MESSAGE_QUEUE,
    async_mode='eventlet'
)

# Initialize Celery
celery = make_celery(app)

# Initialize Redis client
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)


@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html', symbols=Config.DEFAULT_SYMBOLS)


@app.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    """Get market data for a symbol"""
    # Fetch from Redis cache
    quote_data = redis_client.get(f"quote:{symbol}")
    candles_data = redis_client.get(f"candles:{symbol}:1")
    sentiment_data = redis_client.get(f"sentiment:{symbol}")
    
    data = {
        'symbol': symbol,
        'quote': json.loads(quote_data) if quote_data else None,
        'candles': json.loads(candles_data) if candles_data else None,
        'sentiment': json.loads(sentiment_data) if sentiment_data else None
    }
    
    return jsonify(data)


@app.route('/api/signals/<symbol>')
def get_signals(symbol):
    """Get latest trading signals for a symbol"""
    signal_data = redis_client.get(f"signal:{symbol}")
    
    if signal_data:
        return jsonify(json.loads(signal_data))
    else:
        return jsonify({'status': 'no_signal', 'message': 'No active signals'})


@app.route('/api/refresh/<symbol>', methods=['POST'])
def refresh_data(symbol):
    """Trigger data refresh for a symbol"""
    # Queue async tasks
    fetch_quote.delay(symbol)
    fetch_candles.delay(symbol)
    fetch_sentiment.delay(symbol)
    analyze_signal.delay(symbol)
    
    return jsonify({'status': 'success', 'message': f'Data refresh queued for {symbol}'})


@app.route('/api/refresh-all', methods=['POST'])
def refresh_all():
    """Trigger data refresh for all symbols"""
    fetch_all_market_data.delay(Config.DEFAULT_SYMBOLS)
    
    for symbol in Config.DEFAULT_SYMBOLS:
        analyze_signal.delay(symbol)
    
    return jsonify({'status': 'success', 'message': 'Data refresh queued for all symbols'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'status': 'connected'})


@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription to symbol updates"""
    symbol = data.get('symbol')
    print(f'Client subscribed to {symbol}')
    emit('subscribed', {'symbol': symbol, 'status': 'subscribed'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


def redis_listener():
    """Listen to Redis pub/sub and broadcast to WebSocket clients"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('market_data', 'trade_signals', 'trade_executions')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                channel = message['channel']
                
                # Broadcast to all connected clients
                socketio.emit(channel, data)
            except Exception as e:
                print(f"Error broadcasting message: {e}")


# Start Redis listener in background
def start_background_tasks():
    """Start background tasks"""
    socketio.start_background_task(redis_listener)


if __name__ == '__main__':
    start_background_tasks()
    socketio.run(app, host='0.0.0.0', port=5000, debug=Config.DEBUG)
