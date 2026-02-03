# Bhagauti v2 - Advanced Trading System

A powerful trading system with live trading and backtesting capabilities.

## Key Features

- **Live Trading**: Real-time execution with WebSocket-driven price updates
- **Backtesting Engine**: High-fidelity simulation using historical candlestick data to validate strategies before deployment
- **Strategy Framework**: Pluggable strategy interface with built-in examples
- **Risk Management**: Position tracking and portfolio management
- **Flexible Configuration**: Environment-based configuration with API key support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JapjotS/upgraded_bhagauti.git
cd upgraded_bhagauti
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API credentials and settings
```

## Quick Start

### Live Trading

Run the live trading example with mock data:

```bash
python examples/live_trading_example.py
```

This demonstrates:
- Real-time WebSocket price updates
- Order submission and execution
- Portfolio tracking and P&L calculation

### Backtesting

Run the backtesting example:

```bash
python examples/backtesting_example.py
```

This demonstrates:
- Historical candlestick data simulation
- Multiple strategy comparison (Buy & Hold vs SMA Crossover)
- Performance metrics and analysis

## Architecture

### Core Components

- **models.py**: Data models (Order, Trade, Candle, Position, Portfolio)
- **websocket_client.py**: WebSocket client for live price feeds
- **live_trading.py**: Live trading engine with real-time execution
- **backtesting.py**: Backtesting engine for strategy validation
- **strategy.py**: Strategy interface and example implementations
- **config.py**: Configuration management

### Trading Strategies

The system includes two built-in strategies:

1. **Buy and Hold**: Simple long-only strategy
2. **SMA Crossover**: Moving average crossover strategy

Create custom strategies by extending the `Strategy` base class:

```python
from bhagauti.strategy import Strategy
from bhagauti.models import Candle, Order

class MyStrategy(Strategy):
    def on_candle(self, candle: Candle, engine) -> Optional[List[Order]]:
        # Your strategy logic here
        pass
```

## Usage Examples

### Live Trading with Custom Strategy

```python
import asyncio
from bhagauti.config import Config
from bhagauti.live_trading import LiveTradingEngine
from bhagauti.websocket_client import MockWebSocketClient
from bhagauti.strategy import SimpleMovingAverageCrossover

async def main():
    config = Config.from_env()
    ws_client = MockWebSocketClient(symbol=config.symbol)
    engine = LiveTradingEngine(ws_client, config.initial_capital)
    
    strategy = SimpleMovingAverageCrossover(symbol=config.symbol)
    await engine.start()

asyncio.run(main())
```

### Backtesting with Historical Data

```python
from bhagauti.backtesting import BacktestingEngine
from bhagauti.strategy import BuyAndHold

engine = BacktestingEngine(initial_capital=10000)
strategy = BuyAndHold(symbol="BTCUSDT")

# Load your historical candles
candles = load_historical_data()

results = engine.run(candles, lambda eng, candle: strategy.on_candle(candle, eng))
print(f"Return: {results['total_return_pct']:.2f}%")
```

## Configuration

Edit `.env` file to configure:

- `API_KEY`: Your exchange API key
- `API_SECRET`: Your exchange API secret
- `SYMBOL`: Trading symbol (e.g., BTCUSDT)
- `INITIAL_CAPITAL`: Starting capital for trading
- `MAX_POSITION_SIZE`: Maximum position size (0.0 to 1.0)
- `WEBSOCKET_URL`: WebSocket endpoint URL
- `REST_API_URL`: REST API endpoint URL

## Development

### Project Structure

```
upgraded_bhagauti/
├── bhagauti/              # Main package
│   ├── __init__.py
│   ├── models.py          # Data models
│   ├── websocket_client.py # WebSocket client
│   ├── live_trading.py    # Live trading engine
│   ├── backtesting.py     # Backtesting engine
│   ├── strategy.py        # Strategy framework
│   └── config.py          # Configuration
├── examples/              # Example scripts
│   ├── live_trading_example.py
│   └── backtesting_example.py
├── requirements.txt       # Dependencies
├── .env.example          # Example configuration
└── README.md             # Documentation
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
