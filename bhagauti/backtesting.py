"""Backtesting engine for strategy validation using historical data."""
import logging
from datetime import datetime
from typing import List, Optional

from .models import Candle, Order, OrderSide, OrderStatus, OrderType, Position, Portfolio, Trade

logger = logging.getLogger(__name__)


class BacktestingEngine:
    """High-fidelity backtesting engine using historical candlestick data."""
    
    def __init__(
        self,
        initial_capital: float,
        commission_rate: float = 0.001
    ):
        """
        Initialize backtesting engine.
        
        Args:
            initial_capital: Starting capital
            commission_rate: Commission rate per trade (default 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        
        # Portfolio state
        self.portfolio = Portfolio(
            cash=initial_capital,
            positions={},
            timestamp=datetime.now()
        )
        
        # Backtesting state
        self.current_candle: Optional[Candle] = None
        self.executed_trades = []
        self.equity_curve = []
        
    def reset(self):
        """Reset backtest state."""
        self.portfolio = Portfolio(
            cash=self.initial_capital,
            positions={},
            timestamp=datetime.now()
        )
        self.current_candle = None
        self.executed_trades = []
        self.equity_curve = []
        
    def execute_order(self, order: Order, candle: Candle) -> bool:
        """
        Execute an order at the given candle.
        
        Args:
            order: Order to execute
            candle: Current candle for execution
            
        Returns:
            True if order was executed, False otherwise
        """
        # Determine execution price based on order type
        if order.order_type == OrderType.MARKET:
            # Market orders execute at the close price
            execution_price = candle.close
        elif order.order_type == OrderType.LIMIT and order.price:
            # Limit orders execute only if price is within candle range
            if order.side == OrderSide.BUY:
                # Buy limit: execute if candle low is at or below limit price
                if candle.low <= order.price:
                    execution_price = min(order.price, candle.close)
                else:
                    return False
            else:  # SELL
                # Sell limit: execute if candle high is at or above limit price
                if candle.high >= order.price:
                    execution_price = max(order.price, candle.close)
                else:
                    return False
        else:
            return False
            
        # Calculate commission
        commission = order.quantity * execution_price * self.commission_rate
        
        if order.side == OrderSide.BUY:
            total_cost = order.quantity * execution_price + commission
            
            if total_cost > self.portfolio.cash:
                logger.warning(f"Insufficient funds for order: {order}")
                order.status = OrderStatus.REJECTED
                return False
                
            # Deduct from cash
            self.portfolio.cash -= total_cost
            
            # Add or update position
            if order.symbol in self.portfolio.positions:
                pos = self.portfolio.positions[order.symbol]
                # Update average entry price
                total_quantity = pos.quantity + order.quantity
                pos.entry_price = (
                    (pos.entry_price * pos.quantity + execution_price * order.quantity)
                    / total_quantity
                )
                pos.quantity = total_quantity
                pos.current_price = execution_price
            else:
                self.portfolio.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    entry_price=execution_price,
                    current_price=execution_price,
                    timestamp=candle.timestamp
                )
                
        else:  # SELL
            if order.symbol not in self.portfolio.positions:
                logger.warning(f"No position to sell: {order}")
                order.status = OrderStatus.REJECTED
                return False
                
            pos = self.portfolio.positions[order.symbol]
            if pos.quantity < order.quantity:
                logger.warning(f"Insufficient quantity to sell: {order}")
                order.status = OrderStatus.REJECTED
                return False
                
            # Add to cash
            revenue = order.quantity * execution_price - commission
            self.portfolio.cash += revenue
            
            # Update or remove position
            pos.quantity -= order.quantity
            if pos.quantity <= 0:
                del self.portfolio.positions[order.symbol]
        
        # Mark order as filled
        order.status = OrderStatus.FILLED
        order.filled_price = execution_price
        order.timestamp = candle.timestamp
        
        # Record trade
        trade = Trade(
            order_id=order.order_id or f"trade_{len(self.executed_trades)}",
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            timestamp=candle.timestamp,
            commission=commission
        )
        self.executed_trades.append(trade)
        
        logger.info(
            f"[{candle.timestamp}] Order executed: {order.side.value} "
            f"{order.quantity} {order.symbol} @ ${execution_price:.2f}"
        )
        
        return True
        
    def run(self, candles: List[Candle], strategy_func) -> dict:
        """
        Run backtest on historical candle data.
        
        Args:
            candles: List of historical candles
            strategy_func: Strategy function that takes (engine, candle) and returns orders
            
        Returns:
            Backtest results dictionary
        """
        self.reset()
        
        logger.info(f"Starting backtest with {len(candles)} candles")
        
        for candle in candles:
            self.current_candle = candle
            
            # Update current prices for all positions with current candle close price
            # This assumes all candles in a backtest are for the same symbol
            for pos in self.portfolio.positions.values():
                pos.current_price = candle.close
            
            # Get orders from strategy
            orders = strategy_func(self, candle)
            if orders is None:
                orders = []
            elif not isinstance(orders, list):
                orders = [orders]
                
            # Execute orders
            for order in orders:
                self.execute_order(order, candle)
                
            # Record equity curve
            self.equity_curve.append({
                "timestamp": candle.timestamp,
                "cash": self.portfolio.cash,
                "total_value": self.portfolio.total_value,
                "pnl": self.portfolio.total_pnl
            })
        
        # Calculate results
        results = self._calculate_results()
        
        logger.info(f"Backtest completed: {len(self.executed_trades)} trades executed")
        logger.info(f"Final portfolio value: ${self.portfolio.total_value:.2f}")
        logger.info(f"Total PnL: ${results['total_pnl']:.2f} ({results['total_return_pct']:.2f}%)")
        
        return results
        
    def _calculate_results(self) -> dict:
        """Calculate backtest results."""
        if not self.equity_curve:
            return {}
            
        final_value = self.portfolio.total_value
        total_pnl = final_value - self.initial_capital
        total_return_pct = (total_pnl / self.initial_capital) * 100
        
        # Note: Win rate calculation would require tracking buy/sell pairs
        # For now, we just count total trades
        total_trades = len(self.executed_trades)
        
        # Calculate max drawdown
        max_value = self.initial_capital
        max_drawdown = 0
        for point in self.equity_curve:
            value = point["total_value"]
            max_value = max(max_value, value)
            drawdown = (max_value - value) / max_value if max_value > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_pnl": total_pnl,
            "total_return_pct": total_return_pct,
            "total_trades": total_trades,
            "max_drawdown_pct": max_drawdown * 100,
            "equity_curve": self.equity_curve
        }
