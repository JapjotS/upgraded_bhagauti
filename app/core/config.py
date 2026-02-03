import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Redis configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # API Keys
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    MASSIVE_API_KEY = os.getenv('MASSIVE_API_KEY', '')
    
    # Trading settings
    DEFAULT_SYMBOLS = os.getenv('DEFAULT_SYMBOLS', 'AAPL,MSFT,GOOGL').split(',')
    CANDLE_INTERVAL = os.getenv('CANDLE_INTERVAL', '1')  # 1 minute candles
    
    # WebSocket settings
    SOCKETIO_MESSAGE_QUEUE = REDIS_URL
