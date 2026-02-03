#!/usr/bin/env python3
"""
Demo script to showcase the Upgraded Bhagauti trading system
This runs without requiring Redis to be installed
"""

import sys
import time
from datetime import datetime

# Add color support for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def main():
    print_header("=" * 60)
    print_header("⚡ Upgraded Bhagauti Trading System - Demo ⚡")
    print_header("=" * 60)
    
    # Import and test components
    print_header("\n1. Testing Core Components")
    
    try:
        from app.core.config import Config
        print_success("Configuration module loaded")
        print_info(f"   Default symbols: {', '.join(Config.DEFAULT_SYMBOLS)}")
        print_info(f"   Redis URL: {Config.REDIS_URL}")
    except Exception as e:
        print_warning(f"Configuration error: {e}")
        return
    
    try:
        from app.strategies.momentum_strategy import MomentumStrategy
        print_success("Trading strategy loaded")
    except Exception as e:
        print_warning(f"Strategy error: {e}")
        return
    
    # Test strategy with mock data
    print_header("\n2. Testing Momentum Strategy")
    
    strategy = MomentumStrategy(threshold=0.02, volume_threshold=1.5)
    
    # Create realistic mock data for different scenarios
    test_cases = [
        {
            'name': 'Strong Upward Momentum',
            'quote': {
                'current_price': 155.0,
                'percent_change': 3.5,
                'volume': 2000000
            },
            'candles': {
                'close': [140, 142, 145, 146, 148, 147, 149, 148, 150, 151],
                'volume': [500000, 520000, 480000, 510000, 490000, 530000, 500000, 520000, 510000, 2000000],
                'timestamps': list(range(10))
            },
            'sentiment': {'sentiment_score': 0.85}
        },
        {
            'name': 'Strong Downward Momentum',
            'quote': {
                'current_price': 135.0,
                'percent_change': -4.2,
                'volume': 2500000
            },
            'candles': {
                'close': [150, 149, 148, 147, 146, 145, 143, 141, 138, 136],
                'volume': [500000, 520000, 530000, 510000, 490000, 540000, 600000, 800000, 1200000, 2500000],
                'timestamps': list(range(10))
            },
            'sentiment': {'sentiment_score': 0.25}
        },
        {
            'name': 'Neutral/Sideways Movement',
            'quote': {
                'current_price': 148.5,
                'percent_change': 0.3,
                'volume': 800000
            },
            'candles': {
                'close': [148, 149, 147, 148, 149, 147, 148, 149, 148, 148],
                'volume': [1000000, 950000, 1050000, 980000, 1020000, 990000, 1010000, 980000, 1030000, 800000],
                'timestamps': list(range(10))
            },
            'sentiment': {'sentiment_score': 0.50}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}Scenario {i}: {test_case['name']}{Colors.ENDC}")
        print("-" * 60)
        
        signal = strategy.generate_signal(
            'TEST',
            test_case['quote'],
            test_case['candles'],
            test_case['sentiment']
        )
        
        # Display signal
        action_color = Colors.OKGREEN if signal['action'] == 'BUY' else (
            Colors.FAIL if signal['action'] == 'SELL' else Colors.WARNING
        )
        
        print(f"Symbol:     TEST")
        print(f"Price:      ${test_case['quote']['current_price']:.2f}")
        print(f"Change:     {test_case['quote']['percent_change']:+.2f}%")
        print(f"Action:     {action_color}{Colors.BOLD}{signal['action']}{Colors.ENDC}")
        print(f"Confidence: {signal['confidence']:.1%}")
        print(f"Reason:     {signal['reason']}")
        
        if signal['action'] != 'HOLD':
            print(f"Entry:      ${signal.get('entry_price', 0):.2f}")
            print(f"Target:     ${signal.get('target_price', 0):.2f}")
            print(f"Stop Loss:  ${signal.get('stop_loss', 0):.2f}")
        
        time.sleep(0.5)
    
    # Show API client structure
    print_header("\n3. API Integration Overview")
    
    try:
        from app.api.finnhub_client import FinnhubClient
        from app.api.massive_client import MassiveAPIClient
        
        print_success("Finnhub API client initialized")
        print_info("   Provides: Real-time quotes, candle data, company profiles")
        
        print_success("Massive API client initialized")
        print_info("   Provides: Market sentiment, news, technical indicators")
    except Exception as e:
        print_warning(f"API client error: {e}")
    
    # Show system architecture
    print_header("\n4. System Architecture")
    print("""
    ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
    │   Finnhub   │────▶│    Celery    │────▶│    Redis    │
    │     API     │     │   Workers    │     │   Message   │
    └─────────────┘     └──────────────┘     │   Broker    │
                                             └─────────────┘
    ┌─────────────┐     ┌──────────────┐            │
    │   Massive   │────▶│   Strategy   │            │
    │     API     │     │   Engine     │            │
    └─────────────┘     └──────────────┘            │
                                │                   │
                                ▼                   ▼
                        ┌──────────────┐     ┌─────────────┐
                        │    Flask     │────▶│  WebSocket  │
                        │     API      │     │   Clients   │
                        └──────────────┘     └─────────────┘
    """)
    
    print_header("\n5. Key Features")
    features = [
        "✨ Asynchronous task processing with Celery",
        "⚡ Redis for blazing-fast message brokering",
        "📊 Real-time WebSocket updates",
        "🎯 Momentum-based trading strategy",
        "🎨 Modern, animated UI dashboard",
        "🔄 Non-blocking data ingestion",
        "📈 Live market data from Finnhub",
        "🧠 Market sentiment analysis",
        "🚀 Horizontally scalable architecture"
    ]
    
    for feature in features:
        print(f"  {feature}")
        time.sleep(0.1)
    
    print_header("\n6. Next Steps")
    print("""
    To run the full system:
    
    1. Install Redis:
       Ubuntu/Debian: sudo apt-get install redis-server
       macOS:         brew install redis
    
    2. Get API keys:
       Finnhub: https://finnhub.io/ (free tier available)
    
    3. Configure .env file:
       cp .env.example .env
       # Edit .env and add your API keys
    
    4. Start the system:
       Docker:  docker-compose up
       Manual:  ./start.sh
    
    5. Access dashboard:
       Open http://localhost:5000 in your browser
    """)
    
    print_header("=" * 60)
    print_header("Demo completed successfully! 🎉")
    print_header("=" * 60)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Demo interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
