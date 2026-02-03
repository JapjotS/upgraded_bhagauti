"""Tests for backtesting engine."""
import unittest
from datetime import datetime, timedelta

from bhagauti.backtesting import BacktestingEngine
from bhagauti.models import Candle, Order, OrderSide, OrderType
from bhagauti.strategy import BuyAndHold


class TestBacktestingEngine(unittest.TestCase):
    """Test BacktestingEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = BacktestingEngine(initial_capital=10000.0)
        
    def test_initial_state(self):
        """Test initial engine state."""
        self.assertEqual(self.engine.portfolio.cash, 10000.0)
        self.assertEqual(len(self.engine.portfolio.positions), 0)
        self.assertEqual(len(self.engine.executed_trades), 0)
    
    def test_buy_order_execution(self):
        """Test executing a buy order."""
        candle = Candle(
            timestamp=datetime.now(),
            open=50000.0,
            high=50500.0,
            low=49500.0,
            close=50000.0,
            volume=100.0
        )
        
        order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.1
        )
        
        result = self.engine.execute_order(order, candle)
        
        self.assertTrue(result)
        self.assertEqual(len(self.engine.portfolio.positions), 1)
        self.assertIn("BTCUSDT", self.engine.portfolio.positions)
        self.assertLess(self.engine.portfolio.cash, 10000.0)
    
    def test_sell_order_execution(self):
        """Test executing a sell order."""
        # First buy
        buy_candle = Candle(
            timestamp=datetime.now(),
            open=50000.0,
            high=50500.0,
            low=49500.0,
            close=50000.0,
            volume=100.0
        )
        
        buy_order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.1
        )
        
        self.engine.execute_order(buy_order, buy_candle)
        
        # Then sell
        sell_candle = Candle(
            timestamp=datetime.now() + timedelta(hours=1),
            open=52000.0,
            high=52500.0,
            low=51500.0,
            close=52000.0,
            volume=100.0
        )
        
        sell_order = Order(
            symbol="BTCUSDT",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=0.1
        )
        
        result = self.engine.execute_order(sell_order, sell_candle)
        
        self.assertTrue(result)
        self.assertEqual(len(self.engine.portfolio.positions), 0)
        self.assertGreater(self.engine.portfolio.cash, 10000.0 - 5000.0)  # Profit after buy
    
    def test_insufficient_funds(self):
        """Test order rejection due to insufficient funds."""
        candle = Candle(
            timestamp=datetime.now(),
            open=50000.0,
            high=50500.0,
            low=49500.0,
            close=50000.0,
            volume=100.0
        )
        
        order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10.0  # Too much
        )
        
        result = self.engine.execute_order(order, candle)
        
        self.assertFalse(result)
        self.assertEqual(len(self.engine.portfolio.positions), 0)
    
    def test_limit_order_execution(self):
        """Test limit order execution."""
        candle = Candle(
            timestamp=datetime.now(),
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=100.0
        )
        
        # Buy limit at 49500 - should execute
        buy_order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=0.1,
            price=49500.0
        )
        
        result = self.engine.execute_order(buy_order, candle)
        self.assertTrue(result)
        
    def test_limit_order_no_execution(self):
        """Test limit order not executing when price not met."""
        candle = Candle(
            timestamp=datetime.now(),
            open=50000.0,
            high=51000.0,
            low=49500.0,
            close=50500.0,
            volume=100.0
        )
        
        # Buy limit at 49000 - should NOT execute (low only 49500)
        buy_order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=0.1,
            price=49000.0
        )
        
        result = self.engine.execute_order(buy_order, candle)
        self.assertFalse(result)
    
    def test_backtest_run(self):
        """Test running a backtest."""
        # Generate sample candles
        candles = []
        base_price = 50000.0
        start_date = datetime.now() - timedelta(days=10)
        
        for i in range(100):
            candle = Candle(
                timestamp=start_date + timedelta(hours=i),
                open=base_price,
                high=base_price * 1.01,
                low=base_price * 0.99,
                close=base_price,
                volume=100.0
            )
            candles.append(candle)
        
        # Use Buy and Hold strategy
        strategy = BuyAndHold(symbol="BTCUSDT", allocation=0.95)
        
        results = self.engine.run(candles, lambda eng, candle: strategy.on_candle(candle, eng))
        
        self.assertIn("initial_capital", results)
        self.assertIn("final_value", results)
        self.assertIn("total_pnl", results)
        self.assertIn("total_return_pct", results)
        self.assertEqual(results["initial_capital"], 10000.0)


if __name__ == "__main__":
    unittest.main()
