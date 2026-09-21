import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Market Data (Binance Public API - no key needed)
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"
    
    # Assets to scan (Binance symbols)
    ASSETS = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "LINKUSDT", "AVAXUSDT", "MATICUSDT"
    ]
    
    # Timeframe (1m = 1 minute)
    TIMEFRAME = "1m"
    CANDLE_LIMIT = 100  # Number of candles to fetch
    
    # Signal Settings
    MIN_CONFIDENCE = 60  # Minimum confidence percentage
    MAX_SIGNALS_PER_CYCLE = 5  # Max signals to send per cycle
    
    # Scan interval (seconds)
    SCAN_INTERVAL = 60  # 1 minute
    
    # Timezone
    TIMEZONE_OFFSET = 6  # UTC+6
