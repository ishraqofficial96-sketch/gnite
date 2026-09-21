import requests
import pandas as pd
from datetime import datetime
from config import Config
from utils import get_utc_plus_6_time, format_time

class DataFetcher:
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.BINANCE_BASE_URL
    
    def fetch_candles(self, symbol):
        """Fetch candle data from Binance public API"""
        try:
            params = {
                "symbol": symbol,
                "interval": self.config.TIMEFRAME,
                "limit": self.config.CANDLE_LIMIT
            }
            
            response = requests.get(
                f"{self.base_url}/klines",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Convert timestamps
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def check_data_freshness(self, df):
        """Check if the latest candle is fresh"""
        if df is None or df.empty:
            return False
        
        latest_close_time = df.iloc[-1]['close_time']
        now = pd.Timestamp.now(tz='UTC')
        
        # Check if latest candle is within 2 minutes
        time_diff = (now - latest_close_time).total_seconds()
        return time_diff < 120  # 2 minutes
    
    def get_quality_score(self, df):
        """Calculate data quality score"""
        if df is None or df.empty:
            return 0
        
        score = 100
        
        # Check for missing candles
        expected_candles = self.config.CANDLE_LIMIT
        actual_candles = len(df)
        
        if actual_candles < expected_candles * 0.9:
            score -= 30
        elif actual_candles < expected_candles * 0.95:
            score -= 15
        
        # Check for zero values
        zero_values = (df[['open', 'high', 'low', 'close']] == 0).sum().sum()
        if zero_values > 0:
            score -= 20
        
        # Check freshness
        if not self.check_data_freshness(df):
            score -= 25
        
        return max(0, score)
