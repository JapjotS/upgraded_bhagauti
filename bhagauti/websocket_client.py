"""WebSocket client for real-time price updates."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Callable, Optional

import websockets

from .models import Candle

logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client for live price feeds."""
    
    def __init__(self, url: str, symbol: str):
        """
        Initialize WebSocket client.
        
        Args:
            url: WebSocket URL
            symbol: Trading symbol (e.g., 'btcusdt')
        """
        self.url = url
        self.symbol = symbol.lower()
        self.ws = None
        self.running = False
        self._price_callback: Optional[Callable] = None
        self._candle_callback: Optional[Callable] = None
        
    def on_price(self, callback: Callable[[str, float], None]):
        """Register callback for price updates."""
        self._price_callback = callback
        
    def on_candle(self, callback: Callable[[Candle], None]):
        """Register callback for candle updates."""
        self._candle_callback = callback
    
    async def connect(self):
        """Connect to WebSocket."""
        # Subscribe to ticker stream for price updates
        stream = f"{self.symbol}@ticker"
        full_url = f"{self.url}/{stream}"
        
        logger.info(f"Connecting to WebSocket: {full_url}")
        self.ws = await websockets.connect(full_url)
        self.running = True
        logger.info("WebSocket connected")
        
    async def start(self):
        """Start listening for messages."""
        if not self.ws:
            await self.connect()
            
        try:
            async for message in self.ws:
                if not self.running:
                    break
                    
                data = json.loads(message)
                await self._handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.close()
    
    async def _handle_message(self, data: dict):
        """Handle incoming WebSocket message."""
        try:
            # Handle ticker data
            if 'c' in data:  # Current price
                price = float(data['c'])
                if self._price_callback:
                    self._price_callback(self.symbol.upper(), price)
                    
            # Can be extended to handle kline/candle data
            if 'k' in data:  # Kline data
                kline = data['k']
                candle = Candle(
                    timestamp=datetime.fromtimestamp(kline['t'] / 1000),
                    open=float(kline['o']),
                    high=float(kline['h']),
                    low=float(kline['l']),
                    close=float(kline['c']),
                    volume=float(kline['v'])
                )
                if self._candle_callback:
                    self._candle_callback(candle)
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def close(self):
        """Close WebSocket connection."""
        self.running = False
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket closed")


class MockWebSocketClient(WebSocketClient):
    """Mock WebSocket client for testing and backtesting."""
    
    def __init__(self, symbol: str, initial_price: float = 50000.0):
        """
        Initialize mock WebSocket client.
        
        Args:
            symbol: Trading symbol
            initial_price: Starting price for simulation
        """
        super().__init__("mock://localhost", symbol)
        self.current_price = initial_price
        self.price_volatility = 0.001  # 0.1% price movement
        
    async def connect(self):
        """Mock connection (no actual connection needed)."""
        self.running = True
        logger.info("Mock WebSocket connected")
        
    async def start(self):
        """Simulate price updates."""
        self.running = True
        
        try:
            while self.running:
                # Simulate price movement
                import random
                change = random.uniform(-self.price_volatility, self.price_volatility)
                self.current_price *= (1 + change)
                
                if self._price_callback:
                    self._price_callback(self.symbol.upper(), self.current_price)
                
                await asyncio.sleep(1)  # Update every second
                
        except asyncio.CancelledError:
            logger.info("Mock WebSocket cancelled")
        finally:
            await self.close()
    
    async def close(self):
        """Close mock connection."""
        self.running = False
        logger.info("Mock WebSocket closed")
