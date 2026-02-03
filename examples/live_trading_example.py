"""Example: Live trading with mock WebSocket."""
import asyncio
import logging

from bhagauti.config import Config
from bhagauti.live_trading import LiveTradingEngine
from bhagauti.models import Order, OrderSide, OrderType
from bhagauti.strategy import SimpleMovingAverageCrossover
from bhagauti.websocket_client import MockWebSocketClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run live trading example with mock data."""
    # Load configuration
    config = Config.from_env()
    
    # Create mock WebSocket client (simulates real-time price updates)
    ws_client = MockWebSocketClient(symbol=config.symbol, initial_price=50000.0)
    
    # Create live trading engine
    engine = LiveTradingEngine(
        ws_client=ws_client,
        initial_capital=config.initial_capital,
        commission_rate=config.commission_rate
    )
    
    # Create strategy
    strategy = SimpleMovingAverageCrossover(symbol=config.symbol)
    
    logger.info("Starting live trading engine...")
    logger.info(f"Initial capital: ${config.initial_capital}")
    logger.info(f"Symbol: {config.symbol}")
    
    # Start engine in background
    engine_task = asyncio.create_task(engine.start())
    
    # Simulate some trading activity
    try:
        for i in range(30):  # Run for 30 seconds
            await asyncio.sleep(1)
            
            # Print status every 5 seconds
            if i % 5 == 0:
                status = engine.get_portfolio_status()
                logger.info(f"Portfolio value: ${status['total_value']:.2f}")
                if status['positions']:
                    for symbol, pos in status['positions'].items():
                        logger.info(
                            f"  {symbol}: {pos['quantity']:.6f} @ ${pos['current_price']:.2f} "
                            f"(PnL: ${pos['pnl']:.2f}, {pos['pnl_percent']:.2f}%)"
                        )
            
            # Example: Submit a market order after 5 seconds
            if i == 5:
                order = Order(
                    symbol=config.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=0.001
                )
                engine.submit_order(order)
                logger.info(f"Submitted order: {order}")
                
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await engine.stop()
        engine_task.cancel()
        
    # Final status
    final_status = engine.get_portfolio_status()
    logger.info("\n=== Final Portfolio Status ===")
    logger.info(f"Cash: ${final_status['cash']:.2f}")
    logger.info(f"Total Value: ${final_status['total_value']:.2f}")
    logger.info(f"Total PnL: ${final_status['total_pnl']:.2f}")
    logger.info(f"Trades executed: {len(engine.executed_trades)}")


if __name__ == "__main__":
    asyncio.run(main())
