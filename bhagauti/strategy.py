"""Trading strategy interface and example strategies."""
from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Candle, Order, OrderSide, OrderType


class Strategy(ABC):
    """Base class for trading strategies."""
    
    @abstractmethod
    def on_candle(self, candle: Candle, engine) -> Optional[List[Order]]:
        """
        Process a candle and generate orders.
        
        Args:
            candle: Current candle
            engine: Trading engine (LiveTradingEngine or BacktestingEngine)
            
        Returns:
            List of orders to execute, or None
        """
        pass


class SimpleMovingAverageCrossover(Strategy):
    """Simple moving average crossover strategy."""
    
    def __init__(self, symbol: str, fast_period: int = 10, slow_period: int = 20):
        """
        Initialize SMA crossover strategy.
        
        Args:
            symbol: Trading symbol
            fast_period: Fast moving average period
            slow_period: Slow moving average period
        """
        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.prices = []
        self.position = None
        
    def on_candle(self, candle: Candle, engine) -> Optional[List[Order]]:
        """Generate orders based on SMA crossover."""
        self.prices.append(candle.close)
        
        # Need enough data for slow MA
        if len(self.prices) < self.slow_period:
            return None
            
        # Calculate moving averages
        fast_ma = sum(self.prices[-self.fast_period:]) / self.fast_period
        slow_ma = sum(self.prices[-self.slow_period:]) / self.slow_period
        
        orders = []
        
        # Get current position
        has_position = self.symbol in engine.portfolio.positions
        
        # Buy signal: fast MA crosses above slow MA
        if fast_ma > slow_ma and not has_position:
            # Calculate position size (use 10% of portfolio value)
            cash_to_use = engine.portfolio.cash * 0.1
            quantity = cash_to_use / candle.close
            
            if quantity > 0:
                order = Order(
                    symbol=self.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=quantity
                )
                orders.append(order)
                
        # Sell signal: fast MA crosses below slow MA
        elif fast_ma < slow_ma and has_position:
            position = engine.portfolio.positions[self.symbol]
            order = Order(
                symbol=self.symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=position.quantity
            )
            orders.append(order)
            
        return orders if orders else None


class BuyAndHold(Strategy):
    """Simple buy and hold strategy."""
    
    def __init__(self, symbol: str, allocation: float = 1.0):
        """
        Initialize buy and hold strategy.
        
        Args:
            symbol: Trading symbol
            allocation: Portion of capital to invest (0.0 to 1.0)
        """
        self.symbol = symbol
        self.allocation = allocation
        self.bought = False
        
    def on_candle(self, candle: Candle, engine) -> Optional[List[Order]]:
        """Buy once and hold."""
        if not self.bought:
            cash_to_use = engine.portfolio.cash * self.allocation
            quantity = cash_to_use / candle.close
            
            if quantity > 0:
                self.bought = True
                return [Order(
                    symbol=self.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=quantity
                )]
                
        return None
