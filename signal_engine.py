import numpy as np
from utils import calculate_ema, calculate_rsi, calculate_atr

class SignalEngine:
    def __init__(self, min_confidence=60):
        self.min_confidence = min_confidence
    
    def generate_signals(self, data_frames):
        """Generate signals for all assets"""
        signals = []
        
        for symbol, df in data_frames.items():
            if df is None or len(df) < 50:
                continue
            
            signal = self.analyze_asset(symbol, df)
            
            if signal and signal['confidence'] >= self.min_confidence:
                signals.append(signal)
        
        # Sort by confidence (highest first)
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return signals
    
    def analyze_asset(self, symbol, df):
        """Analyze a single asset and generate signal"""
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        
        # Calculate indicators
        ema_fast = calculate_ema(closes, 5)
        ema_slow = calculate_ema(closes, 20)
        rsi = calculate_rsi(closes, 14)
        atr = calculate_atr(highs, lows, closes, 14)
        
        if ema_fast is None or ema_slow is None or rsi is None or atr is None:
            return None
        
        # Get latest values
        latest_close = closes[-1]
        prev_close = closes[-2]
        
        # Signal logic
        direction = None
        confidence = 50
        reasons = []
        
        # EMA Crossover
        if ema_fast > ema_slow and closes[-2] <= calculate_ema(closes[:-1], 20):
            direction = "call"
            confidence += 15
            reasons.append("EMA bullish crossover")
        elif ema_fast < ema_slow and closes[-2] >= calculate_ema(closes[:-1], 20):
            direction = "put"
            confidence += 15
            reasons.append("EMA bearish crossover")
        
        # RSI
        if rsi < 30:
            if direction == "call":
                confidence += 10
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif direction is None:
                direction = "call"
                confidence += 10
                reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            if direction == "put":
                confidence += 10
                reasons.append(f"RSI overbought ({rsi:.1f})")
            elif direction is None:
                direction = "put"
                confidence += 10
                reasons.append(f"RSI overbought ({rsi:.1f})")
        
        # Price action
        if latest_close > prev_close:
            if direction == "call":
                confidence += 5
                reasons.append("Bullish price action")
        else:
            if direction == "put":
                confidence += 5
                reasons.append("Bearish price action")
        
        # ATR volatility check
        if atr > 0:
            volatility = atr / latest_close * 100
            if volatility > 1.5:
                confidence -= 5
                reasons.append(f"High volatility ({volatility:.1f}%)")
        
        # No clear direction
        if direction is None:
            return None
        
        # Cap confidence at 90
        confidence = min(confidence, 90)
        
        # Get current time in UTC+6
        from utils import get_utc_plus_6_time, format_time
        current_time = get_utc_plus_6_time()
        
        return {
            'asset': symbol,
            'direction': direction.upper(),
            'confidence': confidence,
            'price': latest_close,
            'rsi': rsi,
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'atr': atr,
            'reasons': reasons,
            'time': format_time(current_time),
            'entry_window': "30-45 seconds"
        }
