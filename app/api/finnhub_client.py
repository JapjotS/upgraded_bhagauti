import finnhub
from datetime import datetime, timedelta
from app.core.config import Config


class FinnhubClient:
    """Finnhub API client for market data ingestion"""
    
    def __init__(self):
        self.client = finnhub.Client(api_key=Config.FINNHUB_API_KEY)
    
    def get_candles(self, symbol, resolution='1', days_back=1):
        """
        Fetch candle data for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            resolution: Candle resolution (1, 5, 15, 30, 60, D, W, M)
            days_back: Number of days to look back
        
        Returns:
            Dictionary with candle data
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        try:
            candles = self.client.stock_candles(
                symbol,
                resolution,
                int(start_time.timestamp()),
                int(end_time.timestamp())
            )
            
            if candles.get('s') == 'ok':
                return {
                    'symbol': symbol,
                    'timestamps': candles.get('t', []),
                    'open': candles.get('o', []),
                    'high': candles.get('h', []),
                    'low': candles.get('l', []),
                    'close': candles.get('c', []),
                    'volume': candles.get('v', []),
                    'status': 'success'
                }
            else:
                return {'status': 'error', 'message': 'No data available'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_quote(self, symbol):
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with quote data
        """
        try:
            quote = self.client.quote(symbol)
            return {
                'symbol': symbol,
                'current_price': quote.get('c'),
                'change': quote.get('d'),
                'percent_change': quote.get('dp'),
                'high': quote.get('h'),
                'low': quote.get('l'),
                'open': quote.get('o'),
                'previous_close': quote.get('pc'),
                'timestamp': quote.get('t'),
                'status': 'success'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_company_profile(self, symbol):
        """Get company profile information"""
        try:
            profile = self.client.company_profile2(symbol=symbol)
            return {
                'symbol': symbol,
                'name': profile.get('name'),
                'industry': profile.get('finnhubIndustry'),
                'market_cap': profile.get('marketCapitalization'),
                'status': 'success'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
