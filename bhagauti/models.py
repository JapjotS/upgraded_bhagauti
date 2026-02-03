"""Core data models for the trading system."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(Enum):
    """Order sides."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Candle:
    """Candlestick data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def __repr__(self):
        return f"Candle({self.timestamp}, O:{self.open}, H:{self.high}, L:{self.low}, C:{self.close}, V:{self.volume})"


@dataclass
class Order:
    """Trading order."""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    timestamp: Optional[datetime] = None
    filled_price: Optional[float] = None
    order_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Trade:
    """Executed trade."""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    commission: float = 0.0
    
    @property
    def total_value(self) -> float:
        """Total value of the trade including commission."""
        return self.quantity * self.price + self.commission


@dataclass
class Position:
    """Trading position."""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    timestamp: datetime
    
    @property
    def value(self) -> float:
        """Current value of position."""
        return self.quantity * self.current_price
    
    @property
    def pnl(self) -> float:
        """Profit and loss."""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_percent(self) -> float:
        """Profit and loss percentage."""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100


@dataclass
class Portfolio:
    """Portfolio state."""
    cash: float
    positions: dict[str, Position]
    timestamp: datetime
    
    @property
    def total_value(self) -> float:
        """Total portfolio value."""
        positions_value = sum(pos.value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_pnl(self) -> float:
        """Total profit and loss."""
        return sum(pos.pnl for pos in self.positions.values())
