"""Tests for core data models."""
import unittest
from datetime import datetime

from bhagauti.models import (
    Candle, Order, OrderSide, OrderStatus, OrderType,
    Position, Portfolio, Trade
)


class TestCandle(unittest.TestCase):
    """Test Candle model."""
    
    def test_candle_creation(self):
        """Test creating a candle."""
        candle = Candle(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0
        )
        
        self.assertEqual(candle.open, 100.0)
        self.assertEqual(candle.high, 105.0)
        self.assertEqual(candle.low, 95.0)
        self.assertEqual(candle.close, 102.0)
        self.assertEqual(candle.volume, 1000.0)


class TestOrder(unittest.TestCase):
    """Test Order model."""
    
    def test_market_order(self):
        """Test creating a market order."""
        order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.1
        )
        
        self.assertEqual(order.symbol, "BTCUSDT")
        self.assertEqual(order.side, OrderSide.BUY)
        self.assertEqual(order.order_type, OrderType.MARKET)
        self.assertEqual(order.quantity, 0.1)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertIsNotNone(order.timestamp)
    
    def test_limit_order(self):
        """Test creating a limit order."""
        order = Order(
            symbol="BTCUSDT",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=0.1,
            price=50000.0
        )
        
        self.assertEqual(order.price, 50000.0)
        self.assertEqual(order.order_type, OrderType.LIMIT)


class TestPosition(unittest.TestCase):
    """Test Position model."""
    
    def test_position_pnl(self):
        """Test position P&L calculation."""
        position = Position(
            symbol="BTCUSDT",
            quantity=1.0,
            entry_price=50000.0,
            current_price=52000.0,
            timestamp=datetime.now()
        )
        
        self.assertEqual(position.pnl, 2000.0)
        self.assertEqual(position.pnl_percent, 4.0)
        self.assertEqual(position.value, 52000.0)
    
    def test_position_loss(self):
        """Test position with loss."""
        position = Position(
            symbol="BTCUSDT",
            quantity=1.0,
            entry_price=50000.0,
            current_price=48000.0,
            timestamp=datetime.now()
        )
        
        self.assertEqual(position.pnl, -2000.0)
        self.assertEqual(position.pnl_percent, -4.0)


class TestPortfolio(unittest.TestCase):
    """Test Portfolio model."""
    
    def test_empty_portfolio(self):
        """Test empty portfolio."""
        portfolio = Portfolio(
            cash=10000.0,
            positions={},
            timestamp=datetime.now()
        )
        
        self.assertEqual(portfolio.total_value, 10000.0)
        self.assertEqual(portfolio.total_pnl, 0.0)
    
    def test_portfolio_with_positions(self):
        """Test portfolio with positions."""
        position = Position(
            symbol="BTCUSDT",
            quantity=1.0,
            entry_price=50000.0,
            current_price=52000.0,
            timestamp=datetime.now()
        )
        
        portfolio = Portfolio(
            cash=5000.0,
            positions={"BTCUSDT": position},
            timestamp=datetime.now()
        )
        
        self.assertEqual(portfolio.total_value, 57000.0)  # 5000 + 52000
        self.assertEqual(portfolio.total_pnl, 2000.0)


class TestTrade(unittest.TestCase):
    """Test Trade model."""
    
    def test_trade_total_value(self):
        """Test trade total value calculation."""
        trade = Trade(
            order_id="123",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            quantity=1.0,
            price=50000.0,
            timestamp=datetime.now(),
            commission=50.0
        )
        
        self.assertEqual(trade.total_value, 50050.0)


if __name__ == "__main__":
    unittest.main()
