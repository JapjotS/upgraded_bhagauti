#!/usr/bin/env python3
"""
Standalone demo server that runs without Redis for testing the UI
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import random
import time
from threading import Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'

# Mock symbols
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

# Initialize SocketIO without Redis (using threading mode for compatibility)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Mock data generators
def generate_mock_quote(symbol):
    base_price = {'AAPL': 150, 'MSFT': 300, 'GOOGL': 120, 'TSLA': 200, 'AMZN': 130}
    price = base_price.get(symbol, 100) + random.uniform(-5, 5)
    change = random.uniform(-3, 3)
    
    return {
        'symbol': symbol,
        'current_price': price,
        'percent_change': change,
        'volume': random.randint(1000000, 5000000),
        'status': 'success'
    }

def generate_mock_sentiment(symbol):
    return {
        'symbol': symbol,
        'sentiment_score': random.uniform(0.3, 0.9),
        'status': 'success'
    }

def generate_mock_candles(symbol):
    base_price = {'AAPL': 150, 'MSFT': 300, 'GOOGL': 120, 'TSLA': 200, 'AMZN': 130}
    base = base_price.get(symbol, 100)
    
    close_prices = []
    for _ in range(30):
        base += random.uniform(-2, 2)
        close_prices.append(base)
    
    return {
        'symbol': symbol,
        'close': close_prices,
        'timestamps': list(range(30)),
        'status': 'success'
    }

# Background task to send periodic updates
def send_periodic_updates():
    while True:
        time.sleep(3)
        for symbol in SYMBOLS:
            # Send mock market data
            quote = generate_mock_quote(symbol)
            socketio.emit('market_data', {
                'type': 'quote',
                'symbol': symbol,
                'data': quote
            })
            
            # Randomly send signals
            if random.random() > 0.85:
                actions = ['BUY', 'SELL', 'HOLD']
                action = random.choice(actions)
                if action != 'HOLD':
                    signal = {
                        'symbol': symbol,
                        'action': action,
                        'confidence': random.uniform(0.6, 0.95),
                        'reason': f'Demo signal for {symbol}',
                        'timestamp': time.time()
                    }
                    socketio.emit('trade_signals', {
                        'symbol': symbol,
                        'signal': signal
                    })

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html', symbols=SYMBOLS)

@app.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    """Get mock market data for a symbol"""
    return jsonify({
        'symbol': symbol,
        'quote': generate_mock_quote(symbol),
        'candles': generate_mock_candles(symbol),
        'sentiment': generate_mock_sentiment(symbol)
    })

@app.route('/api/signals/<symbol>')
def get_signals(symbol):
    """Get mock signals"""
    return jsonify({
        'symbol': symbol,
        'action': 'HOLD',
        'status': 'no_signal'
    })

@app.route('/api/refresh/<symbol>', methods=['POST'])
def refresh_data(symbol):
    """Mock refresh"""
    # Send immediate updates
    socketio.emit('market_data', {
        'type': 'quote',
        'symbol': symbol,
        'data': generate_mock_quote(symbol)
    })
    socketio.emit('market_data', {
        'type': 'candles',
        'symbol': symbol,
        'data': generate_mock_candles(symbol)
    })
    socketio.emit('market_data', {
        'type': 'sentiment',
        'symbol': symbol,
        'data': generate_mock_sentiment(symbol)
    })
    return jsonify({'status': 'success'})

@app.route('/api/refresh-all', methods=['POST'])
def refresh_all():
    """Mock refresh all"""
    for symbol in SYMBOLS:
        socketio.emit('market_data', {
            'type': 'quote',
            'symbol': symbol,
            'data': generate_mock_quote(symbol)
        })
    return jsonify({'status': 'success'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected to demo server')
    
    # Send initial data
    for symbol in SYMBOLS:
        socketio.emit('market_data', {
            'type': 'quote',
            'symbol': symbol,
            'data': generate_mock_quote(symbol)
        })
        socketio.emit('market_data', {
            'type': 'candles',
            'symbol': symbol,
            'data': generate_mock_candles(symbol)
        })
        socketio.emit('market_data', {
            'type': 'sentiment',
            'symbol': symbol,
            'data': generate_mock_sentiment(symbol)
        })

if __name__ == '__main__':
    # Start background task
    Thread(target=send_periodic_updates, daemon=True).start()
    
    print("=" * 60)
    print("🚀 Demo Server Starting")
    print("=" * 60)
    print("📊 This is a demo server with mock data")
    print("🌐 Open http://localhost:5000 in your browser")
    print("=" * 60)
    
    # WARNING: allow_unsafe_werkzeug=True is only safe for development/demo
    # Never use this in production - use a proper WSGI server like gunicorn
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
