"""Live trading engine with real-time execution."""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from .models import Order, OrderSide, OrderStatus, OrderType, Position, Portfolio, Trade
from .websocket_client import WebSocketClient

logger = logging.getLogger(__name__)


class LiveTradingEngine:
    """Live trading engine with WebSocket-driven price updates."""
    
    def __init__(
        self,
        ws_client: WebSocketClient,
        initial_capital: float,
        commission_rate: float = 0.001
    ):
        """
        Initialize live trading engine.
        
        Args:
            ws_client: WebSocket client for price updates
            initial_capital: Starting capital
            commission_rate: Commission rate per trade (default 0.1%)
        """
        self.ws_client = ws_client
        self.commission_rate = commission_rate
        
        # Portfolio state
        self.portfolio = Portfolio(
            cash=initial_capital,
            positions={},
            timestamp=datetime.now()
        )
        
        # Trading state
        self.current_prices = {}
        self.pending_orders = []
        self.executed_trades = []
        self.running = False
        
        # Set up price callback
        self.ws_client.on_price(self._on_price_update)
        
    def _on_price_update(self, symbol: str, price: float):
        """Handle price updates from WebSocket."""
        self.current_prices[symbol] = price
        
        # Update positions with current prices
        if symbol in self.portfolio.positions:
            self.portfolio.positions[symbol].current_price = price
            
        # Check pending orders
        self._process_pending_orders()
        
        logger.debug(f"Price update: {symbol} = ${price:.2f}")
        
    def _process_pending_orders(self):
        """Process pending orders based on current prices."""
        filled_orders = []
        
        for order in self.pending_orders:
            if order.symbol in self.current_prices:
                current_price = self.current_prices[order.symbol]
                
                # For market orders, fill at current price
                if order.order_type == OrderType.MARKET:
                    self._execute_order(order, current_price)
                    filled_orders.append(order)
                    
                # For limit orders, check if price condition is met
                elif order.order_type == OrderType.LIMIT and order.price:
                    if order.side == OrderSide.BUY and current_price <= order.price:
                        self._execute_order(order, current_price)
                        filled_orders.append(order)
                    elif order.side == OrderSide.SELL and current_price >= order.price:
                        self._execute_order(order, current_price)
                        filled_orders.append(order)
        
        # Remove filled orders from pending
        for order in filled_orders:
            self.pending_orders.remove(order)
            
    def _execute_order(self, order: Order, execution_price: float):
        """Execute an order."""
        commission = order.quantity * execution_price * self.commission_rate
        
        if order.side == OrderSide.BUY:
            total_cost = order.quantity * execution_price + commission
            
            if total_cost > self.portfolio.cash:
                logger.warning(f"Insufficient funds for order: {order}")
                order.status = OrderStatus.REJECTED
                return
                
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
                    timestamp=datetime.now()
                )
                
        else:  # SELL
            if order.symbol not in self.portfolio.positions:
                logger.warning(f"No position to sell: {order}")
                order.status = OrderStatus.REJECTED
                return
                
            pos = self.portfolio.positions[order.symbol]
            if pos.quantity < order.quantity:
                logger.warning(f"Insufficient quantity to sell: {order}")
                order.status = OrderStatus.REJECTED
                return
                
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
        
        # Record trade
        trade = Trade(
            order_id=order.order_id or f"trade_{len(self.executed_trades)}",
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            timestamp=datetime.now(),
            commission=commission
        )
        self.executed_trades.append(trade)
        
        logger.info(f"Order executed: {order.side.value} {order.quantity} {order.symbol} @ ${execution_price:.2f}")
        
    def submit_order(self, order: Order) -> bool:
        """
        Submit an order for execution.
        
        Args:
            order: Order to submit
            
        Returns:
            True if order was accepted, False otherwise
        """
        # Assign order ID if not present
        if not order.order_id:
            order.order_id = f"order_{len(self.pending_orders) + len(self.executed_trades)}"
            
        self.pending_orders.append(order)
        logger.info(f"Order submitted: {order}")
        return True
        
    def get_portfolio_status(self) -> dict:
        """Get current portfolio status."""
        return {
            "cash": self.portfolio.cash,
            "total_value": self.portfolio.total_value,
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "value": pos.value,
                    "pnl": pos.pnl,
                    "pnl_percent": pos.pnl_percent
                }
                for symbol, pos in self.portfolio.positions.items()
            },
            "total_pnl": self.portfolio.total_pnl,
            "timestamp": datetime.now().isoformat()
        }
    
    async def start(self):
        """Start the live trading engine."""
        self.running = True
        logger.info("Starting live trading engine")
        
        # Start WebSocket client in background
        asyncio.create_task(self.ws_client.start())
        
        # Keep running until stopped
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down live trading engine")
            await self.stop()
            
    async def stop(self):
        """Stop the live trading engine."""
        self.running = False
        await self.ws_client.close()
        logger.info("Live trading engine stopped")
