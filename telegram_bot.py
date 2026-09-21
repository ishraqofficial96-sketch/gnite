import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
    
    async def setup_commands(self):
        """Setup bot commands"""
        await self.application.bot.set_my_commands([
            ("start", "Start the bot"),
            ("signal", "Get latest signal"),
            ("stats", "Get bot statistics"),
            ("stop", "Stop the bot")
        ])
    
    async def send_signal(self, signal):
        """Send signal to Telegram"""
        message = (
            f"🚨 **TRADING SIGNAL**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 **Asset:** {signal['asset']}\n"
            f"📈 **Direction:** {'🟢 CALL' if signal['direction'] == 'CALL' else '🔴 PUT'}\n"
            f"🎯 **Confidence:** {signal['confidence']}%\n"
            f"💰 **Price:** ${signal['price']:.4f}\n"
            f"⏰ **Time:** {signal['time']} (UTC+6)\n"
            f"⏱️ **Entry Window:** {signal['entry_window']}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📋 **Reasons:**\n"
        )
        
        for reason in signal['reasons']:
            message += f"• {reason}\n"
        
        message += (
            f"━━━━━━━━━━━━━━━\n"
            f"⚠️ **Risk Warning:** Trade at your own risk. "
            f"Never invest more than you can afford to lose."
        )
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode='Markdown'
        )
    
    async def send_notification(self, message):
        """Send notification to Telegram"""
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode='Markdown'
        )
    
    async def send_signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signal command"""
        await update.message.reply_text(
            "📊 Bot is running. Signals will be sent automatically every minute.\n"
            "Use /start to start receiving signals."
        )
    
    async def send_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        await update.message.reply_text(
            "📈 **Bot Statistics**\n"
            "━━━━━━━━━━━━━━━\n"
            "• Status: Running\n"
            "• Mode: Signal Only (No Auto Trading)\n"
            "• Assets: 10\n"
            "• Timeframe: 1 minute\n"
            "• Min Confidence: 60%"
        )
    
    async def send_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        await update.message.reply_text(
            "🛑 Bot will stop after current cycle."
        )
