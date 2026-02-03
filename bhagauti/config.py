"""Configuration management."""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    
    # API Configuration
    api_key: str
    api_secret: str
    websocket_url: str
    rest_api_url: str
    
    # Trading Configuration
    symbol: str
    initial_capital: float
    max_position_size: float
    commission_rate: float = 0.001
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("API_KEY", ""),
            api_secret=os.getenv("API_SECRET", ""),
            websocket_url=os.getenv("WEBSOCKET_URL", "wss://stream.binance.com:9443/ws"),
            rest_api_url=os.getenv("REST_API_URL", "https://api.binance.com"),
            symbol=os.getenv("SYMBOL", "BTCUSDT"),
            initial_capital=float(os.getenv("INITIAL_CAPITAL", "10000")),
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.1"))
        )
