import asyncio
import logging
from config import Config
from data_fetch import DataFetcher
from signal_engine import SignalEngine
from telegram_bot import TelegramNotifier
from utils import setup_logging, get_utc_plus_6_time, format_time

logger = setup_logging()

class QuotexSignalBot:
    def __init__(self):
        self.config = Config()
        self.data_fetcher = DataFetcher()
        self.signal_engine = SignalEngine(self.config.MIN_CONFIDENCE)
        self.telegram = TelegramNotifier(
            self.config.TELEGRAM_BOT_TOKEN,
            self.config.TELEGRAM_CHAT_ID
        )
        self.running = False
        self.total_signals = 0
    
    async def scan_assets(self):
        """Scan all assets for signals"""
        data_frames = {}
        
        for symbol in self.config.ASSETS:
            df = self.data_fetcher.fetch_candles(symbol)
            
            if df is not None:
                quality = self.data_fetcher.get_quality_score(df)
                if quality >= 70:  # Quality threshold
                    data_frames[symbol] = df
                    logger.info(f"✓ {symbol}: Data quality {quality}%")
                else:
                    logger.warning(f"✗ {symbol}: Low quality data ({quality}%)")
            else:
                logger.warning(f"✗ {symbol}: No data available")
        
        return data_frames
    
    async def process_signals(self):
        """Process signals and send to Telegram only"""
        data_frames = await self.scan_assets()
        
        if len(data_frames) < len(self.config.ASSETS) * 0.5:
            logger.warning("Too many assets with poor data quality")
            await self.telegram.send_notification(
                "⚠️ **Warning:** Too many assets with poor data quality. Skipping this cycle."
            )
            return
        
        signals = self.signal_engine.generate_signals(data_frames)
        
        if not signals:
            logger.info("No signals generated this cycle")
            return
        
        # Send top signals only
        for signal in signals[:self.config.MAX_SIGNALS_PER_CYCLE]:
            await self.telegram.send_signal(signal)
            self.total_signals += 1
            logger.info(
                f"Signal sent: {signal['asset']} {signal['direction']} "
                f"({signal['confidence']}%)"
            )
    
    async def run(self):
        """Main bot loop"""
        logger.info("Starting Quotex Signal Bot...")
        
        await self.telegram.setup_commands()
        
        await self.telegram.send_notification(
            "🤖 **Quotex Signal Bot Started**\n"
            "━━━━━━━━━━━━━━━\n"
            "📊 **Mode:** Signal Only (No Auto Trading)\n"
            "📅 **Time:** " + format_time(get_utc_plus_6_time()) + " (UTC+6)\n"
            "📊 **Assets:** " + str(len(self.config.ASSETS)) + "\n"
            "🎯 **Min Confidence:** " + str(self.config.MIN_CONFIDENCE) + "%\n"
            "━━━━━━━━━━━━━━━\n"
            "✅ Signals will be sent automatically every minute."
        )
        
        self.running = True
        
        while self.running:
            try:
                current_time = get_utc_plus_6_time()
                logger.info(f"Scanning assets at {format_time(current_time)}")
                
                await self.process_signals()
                
                await asyncio.sleep(self.config.SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await self.telegram.send_notification(
                    f"⚠️ **Error:** {str(e)}"
                )
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the bot"""
        self.running = False
        await self.telegram.send_notification(
            "🛑 **Quotex Signal Bot Stopped**\n"
            f"📊 Total signals sent: {self.total_signals}"
        )

async def main():
    bot = QuotexSignalBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
