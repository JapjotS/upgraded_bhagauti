"""Example: Backtesting with historical data."""
import logging
from datetime import datetime, timedelta

from bhagauti.backtesting import BacktestingEngine
from bhagauti.config import Config
from bhagauti.models import Candle
from bhagauti.strategy import SimpleMovingAverageCrossover, BuyAndHold

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def generate_sample_candles(days: int = 100, initial_price: float = 50000.0):
    """Generate sample candlestick data for demonstration."""
    import random
    
    candles = []
    current_price = initial_price
    start_date = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):  # Hourly candles
        timestamp = start_date + timedelta(hours=i)
        
        # Simulate price movement
        change = random.uniform(-0.02, 0.02)  # ±2% change
        current_price *= (1 + change)
        
        open_price = current_price
        close_price = current_price * (1 + random.uniform(-0.01, 0.01))
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.005))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.005))
        volume = random.uniform(100, 1000)
        
        candle = Candle(
            timestamp=timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        )
        candles.append(candle)
        current_price = close_price
    
    return candles


def main():
    """Run backtesting example."""
    # Load configuration
    config = Config.from_env()
    
    logger.info("=== Backtesting Example ===")
    logger.info(f"Initial capital: ${config.initial_capital}")
    logger.info(f"Symbol: {config.symbol}")
    
    # Generate sample historical data
    logger.info("Generating sample historical data...")
    candles = generate_sample_candles(days=100)
    logger.info(f"Generated {len(candles)} candles")
    
    # Create backtesting engine
    engine = BacktestingEngine(
        initial_capital=config.initial_capital,
        commission_rate=config.commission_rate
    )
    
    # Test 1: Buy and Hold strategy
    logger.info("\n--- Testing Buy and Hold Strategy ---")
    strategy = BuyAndHold(symbol=config.symbol, allocation=0.95)
    
    results = engine.run(candles, lambda eng, candle: strategy.on_candle(candle, eng))
    
    logger.info(f"Initial capital: ${results['initial_capital']:.2f}")
    logger.info(f"Final value: ${results['final_value']:.2f}")
    logger.info(f"Total PnL: ${results['total_pnl']:.2f} ({results['total_return_pct']:.2f}%)")
    logger.info(f"Total trades: {results['total_trades']}")
    logger.info(f"Max drawdown: {results['max_drawdown_pct']:.2f}%")
    
    # Test 2: SMA Crossover strategy
    logger.info("\n--- Testing SMA Crossover Strategy ---")
    strategy2 = SimpleMovingAverageCrossover(symbol=config.symbol, fast_period=10, slow_period=20)
    
    results2 = engine.run(candles, lambda eng, candle: strategy2.on_candle(candle, eng))
    
    logger.info(f"Initial capital: ${results2['initial_capital']:.2f}")
    logger.info(f"Final value: ${results2['final_value']:.2f}")
    logger.info(f"Total PnL: ${results2['total_pnl']:.2f} ({results2['total_return_pct']:.2f}%)")
    logger.info(f"Total trades: {results2['total_trades']}")
    logger.info(f"Max drawdown: {results2['max_drawdown_pct']:.2f}%")
    
    # Compare strategies
    logger.info("\n=== Strategy Comparison ===")
    logger.info(f"Buy & Hold return: {results['total_return_pct']:.2f}%")
    logger.info(f"SMA Crossover return: {results2['total_return_pct']:.2f}%")
    
    if results2['total_return_pct'] > results['total_return_pct']:
        logger.info("SMA Crossover outperformed Buy & Hold!")
    else:
        logger.info("Buy & Hold outperformed SMA Crossover!")


if __name__ == "__main__":
    main()
