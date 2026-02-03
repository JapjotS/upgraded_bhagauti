# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Prerequisites
Make sure you have:
- Python 3.9 or higher installed
- Docker and Docker Compose (for easiest setup)
- Finnhub API key (free at https://finnhub.io/)

### 2. Quick Setup with Docker

```bash
# Clone and enter directory
git clone https://github.com/JapjotS/upgraded_bhagauti.git
cd upgraded_bhagauti

# Create environment file
cp .env.example .env

# Edit .env and add your Finnhub API key
nano .env  # or use your favorite editor

# Start everything with Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

That's it! Open http://localhost:5000 in your browser.

### 3. Manual Setup (Without Docker)

```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server

# Install Python dependencies
pip install -r requirements.txt

# Create and configure .env file
cp .env.example .env
nano .env  # Add your API keys

# Use the startup script
./start.sh

# OR start services manually in separate terminals:

# Terminal 1: Celery Worker
celery -A app.core.celery_app worker --loglevel=info

# Terminal 2: Celery Beat (for periodic tasks)
celery -A app.core.celery_app beat --loglevel=info

# Terminal 3: Flask App
python app.py
```

### 4. Configure Your Symbols

Edit `.env` file to change which stocks to track:

```
DEFAULT_SYMBOLS=AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA
```

### 5. Understanding the Dashboard

The dashboard shows:
- **Symbol Cards**: Each card displays a stock with real-time data
- **Price**: Current price and percentage change (green=up, red=down)
- **Volume**: Trading volume (formatted as K, M, or B)
- **Sentiment**: Market sentiment score (0-100%)
- **Chart**: Last 30 price points
- **Signal Badge**: Current trading signal (BUY/SELL/HOLD)
- **Signal Feed**: Live feed of all trading signals on the right

### 6. How It Works

1. **Data Collection**: Celery workers fetch data from Finnhub API every minute
2. **Caching**: Data is stored in Redis for fast access
3. **Analysis**: Trading strategies analyze the data and generate signals
4. **Real-time Updates**: WebSocket pushes updates to your browser instantly
5. **Non-blocking**: Everything runs asynchronously, so nothing blocks

### 7. Customization

#### Add a New Stock Symbol
1. Edit `.env` file
2. Add symbol to `DEFAULT_SYMBOLS`
3. Restart the application

#### Change Update Frequency
Edit `app/tasks/periodic.py`:
```python
# Change from 60 seconds to something else
sender.add_periodic_task(
    30.0,  # Now updates every 30 seconds
    fetch_all_data.s(),
    name='fetch_all_market_data_periodic'
)
```

#### Adjust Strategy Parameters
Edit `app/strategies/momentum_strategy.py`:
```python
# In MomentumStrategy __init__
def __init__(self, threshold=0.03, volume_threshold=2.0):
    # Now requires 3% price change and 2x volume
```

### 8. Monitoring

#### Check Celery Tasks
```bash
# See active workers
celery -A app.core.celery_app status

# Monitor tasks
celery -A app.core.celery_app events
```

#### Check Redis
```bash
# Connect to Redis CLI
redis-cli

# See all keys
KEYS *

# Get a quote
GET quote:AAPL

# Monitor pub/sub
SUBSCRIBE market_data
```

#### View Logs
```bash
# Docker logs
docker-compose logs -f web
docker-compose logs -f celery_worker

# Or check application logs in the console
```

### 9. Troubleshooting

#### "Redis connection refused"
- Make sure Redis is running: `redis-cli ping` should return `PONG`
- Start Redis: `redis-server` or `docker-compose up redis`

#### "No data appearing"
- Check your Finnhub API key in `.env`
- Verify Celery workers are running: `celery -A app.core.celery_app status`
- Check browser console for WebSocket errors

#### "Module not found" errors
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the right directory

### 10. Production Deployment

For production use:

1. Change `SECRET_KEY` in `.env` to a random string
2. Set `DEBUG=False`
3. Use a production WSGI server (gunicorn)
4. Enable HTTPS
5. Add authentication
6. Use a proper Redis instance (not the default)
7. Monitor with tools like Flower for Celery

### 11. Next Steps

- Explore the code in `app/` directory
- Create your own trading strategy in `app/strategies/`
- Add more API integrations
- Enhance the UI with more features
- Add backtesting capabilities

Enjoy trading! 🚀
