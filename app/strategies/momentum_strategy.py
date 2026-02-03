from datetime import datetime


class MomentumStrategy:
    """
    Momentum-based trading strategy
    Generates BUY/SELL/HOLD signals based on price momentum and technical indicators
    """
    
    def __init__(self, threshold=0.02, volume_threshold=1.5):
        self.threshold = threshold  # 2% price change threshold
        self.volume_threshold = volume_threshold
    
    def generate_signal(self, symbol, quote, candles, sentiment=None):
        """
        Generate trading signal based on market data
        
        Args:
            symbol: Stock symbol
            quote: Real-time quote data
            candles: Historical candle data
            sentiment: Market sentiment data (optional)
        
        Returns:
            Dictionary with signal data
        """
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': ''
        }
        
        try:
            current_price = quote.get('current_price', 0)
            percent_change = quote.get('percent_change', 0)
            
            if not current_price or not candles.get('close'):
                signal['reason'] = 'Insufficient data'
                return signal
            
            # Calculate momentum indicators
            close_prices = candles.get('close', [])
            volumes = candles.get('volume', [])
            
            if len(close_prices) < 10:
                signal['reason'] = 'Insufficient historical data'
                return signal
            
            # Simple momentum calculation
            avg_price = sum(close_prices[-10:]) / 10
            price_momentum = (current_price - avg_price) / avg_price
            
            # Volume analysis
            # Use recent volume data, with fallback to candle volumes if available
            avg_volume = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else 1
            current_volume = volumes[-1] if volumes else avg_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Sentiment adjustment
            sentiment_score = sentiment.get('sentiment_score', 0.5) if sentiment else 0.5
            
            # Generate signal
            if price_momentum > self.threshold and volume_ratio > self.volume_threshold:
                signal['action'] = 'BUY'
                signal['confidence'] = min(0.95, 0.5 + price_momentum + (sentiment_score * 0.2))
                signal['reason'] = f'Strong upward momentum ({price_momentum:.2%}) with high volume'
                signal['entry_price'] = current_price
                signal['target_price'] = current_price * 1.05  # 5% target
                signal['stop_loss'] = current_price * 0.97  # 3% stop loss
            
            elif price_momentum < -self.threshold and volume_ratio > self.volume_threshold:
                signal['action'] = 'SELL'
                signal['confidence'] = min(0.95, 0.5 + abs(price_momentum) + ((1 - sentiment_score) * 0.2))
                signal['reason'] = f'Strong downward momentum ({price_momentum:.2%}) with high volume'
                signal['entry_price'] = current_price
                signal['target_price'] = current_price * 0.95  # 5% target
                signal['stop_loss'] = current_price * 1.03  # 3% stop loss
            
            else:
                signal['reason'] = f'No strong momentum (change: {price_momentum:.2%}, volume ratio: {volume_ratio:.2f})'
            
        except Exception as e:
            signal['reason'] = f'Error: {str(e)}'
        
        return signal
    
    def validate_signal(self, signal):
        """Validate signal before execution"""
        if signal['action'] == 'HOLD':
            return False
        if signal['confidence'] < 0.6:
            return False
        return True
