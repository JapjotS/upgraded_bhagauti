# Upgraded Bhagauti ⚡

A high-performance, real-time trading ecosystem built with Python, providing blazing-fast market execution and strategy validation.

## Features

🚀 **High-Performance Architecture**
- Redis as a blazingly fast message broker
- Celery for distributed asynchronous task management
- Non-blocking high-frequency data ingestion
- Real-time trade signals via WebSocket

📊 **Market Data Integration**
- Finnhub API for live market data and candles
- Massive API for sentiment analysis and news
- Asynchronous data fetching to prevent blocking
- Intelligent caching with Redis

💹 **Trading Framework**
- Generalized strategy framework (Momentum strategy included)
- Real-time signal generation
- Trade execution simulation
- Position monitoring

🎨 **Modern UI**
- Sleek, dark-themed dashboard
- Smooth animations and transitions
- Real-time WebSocket updates
- Responsive design
- Interactive charts with Chart.js

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Finnhub   │────▶│    Celery    │────▶│    Redis    │
│     API     │     │   Workers    │     │   Message   │
└─────────────┘     └──────────────┘     │   Broker    │
                                         └─────────────┘
┌─────────────┐     ┌──────────────┐            │
│   Massive   │────▶│   Strategy   │            │
│     API     │     │   Engine     │            │
└─────────────┘     └──────────────┘            │
                            │                   │
                            ▼                   ▼
                    ┌──────────────┐     ┌─────────────┐
                    │    Flask     │────▶│  WebSocket  │
                    │     API      │     │   Clients   │
                    └──────────────┘     └─────────────┘
```

## Installation

### Prerequisites
- Python 3.9+
- Redis
- Docker (optional but recommended)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/JapjotS/upgraded_bhagauti.git
cd upgraded_bhagauti
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```
FINNHUB_API_KEY=your_finnhub_api_key_here
MASSIVE_API_KEY=your_massive_api_key_here
```

4. Start all services with Docker Compose:
```bash
docker-compose up -d
```

5. Access the dashboard at `http://localhost:5000`

### Manual Installation

1. Install Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file and configure API keys (see step 2-3 above)

4. Start Redis:
```bash
redis-server
```

5. Start Celery worker (in a new terminal):
```bash
celery -A app.core.celery_app worker --loglevel=info
```

6. Start the Flask application (in a new terminal):
```bash
python app.py
```

7. Access the dashboard at `http://localhost:5000`

## Configuration

All configuration is done via environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `FINNHUB_API_KEY` | Your Finnhub API key | Required |
| `MASSIVE_API_KEY` | Your Massive API key | Required |
| `REDIS_HOST` | Redis server host | localhost |
| `REDIS_PORT` | Redis server port | 6379 |
| `DEFAULT_SYMBOLS` | Comma-separated stock symbols | AAPL,MSFT,GOOGL,TSLA,AMZN |
| `CANDLE_INTERVAL` | Candle interval in minutes | 1 |
| `SECRET_KEY` | Flask secret key | (auto-generated) |

## Usage

### Dashboard
The main dashboard displays:
- Real-time stock prices
- Price charts with 30-period history
- Trading signals (BUY/SELL/HOLD)
- Market sentiment scores
- Live signal feed

### API Endpoints

- `GET /` - Main dashboard
- `GET /api/market-data/<symbol>` - Get market data for a symbol
- `GET /api/signals/<symbol>` - Get latest trading signals
- `POST /api/refresh/<symbol>` - Trigger data refresh for a symbol
- `POST /api/refresh-all` - Trigger data refresh for all symbols

### WebSocket Events

The application emits real-time events via WebSocket:
- `market_data` - Market data updates (quotes, candles, sentiment)
- `trade_signals` - New trading signals
- `trade_executions` - Trade execution updates

## Trading Strategies

### Momentum Strategy (Included)

The included momentum strategy analyzes:
- Price momentum over 10-period average
- Volume analysis (comparing to 10-period average)
- Market sentiment (if available)

**Signal Generation:**
- **BUY**: Strong upward momentum (>2%) with high volume
- **SELL**: Strong downward momentum (<-2%) with high volume
- **HOLD**: No clear momentum

### Creating Custom Strategies

1. Create a new file in `app/strategies/`
2. Implement the `generate_signal()` method
3. Register your strategy in `app/tasks/trading.py`

Example:
```python
class MyStrategy:
    def generate_signal(self, symbol, quote, candles, sentiment=None):
        # Your strategy logic here
        return {
            'symbol': symbol,
            'action': 'BUY',  # or 'SELL', 'HOLD'
            'confidence': 0.85,
            'reason': 'Your reason here'
        }
```

## Development

### Project Structure
```
upgraded_bhagauti/
├── app/
│   ├── api/              # API clients (Finnhub, Massive)
│   ├── core/             # Core configuration and Celery setup
│   ├── tasks/            # Celery tasks
│   ├── strategies/       # Trading strategies
│   ├── models/           # Data models
│   └── utils/            # Utility functions
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript
├── templates/            # HTML templates
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
└── README.md             # This file
```

### Running Tests
```bash
# Tests can be added in a tests/ directory
pytest
```

## Performance

The application is designed for high-frequency trading with:
- **Non-blocking I/O**: All API calls are asynchronous via Celery
- **Caching**: Redis caches market data to reduce API calls
- **Pub/Sub**: Real-time updates via Redis pub/sub
- **WebSocket**: Efficient real-time communication with clients
- **Distributed Workers**: Scale horizontally by adding Celery workers

## Security Notes

⚠️ **Important Security Considerations:**
- Never commit your `.env` file with real API keys
- Change the `SECRET_KEY` in production
- Use HTTPS in production
- Implement authentication for production use
- Be mindful of API rate limits

## API Keys

### Finnhub API
Get your free API key at: https://finnhub.io/

### Massive API
This is a placeholder integration. Replace with your actual market data API.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.
