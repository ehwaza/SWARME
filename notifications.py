"""
📱 SWARNE V2.0 - Notifications
Système de notifications Telegram et Email
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class TelegramNotifier:
    """Notificateur Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        if not TELEGRAM_AVAILABLE:
            logger.warning("⚠️ python-telegram-bot not installed")
            self.enabled = False
            return
            
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.enabled = True
        
    def send_trade_signal(self, signal: str, price: float, 
                         confidence: float, bee_id: str):
        """Envoyer notification de signal"""
        if not self.enabled:
            return
            
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
        
        message = f"""
{emoji} SWARNE SIGNAL!

Direction: {signal}
Price: {price:.5f}
Confidence: {confidence:.1%}
Bee: {bee_id}

Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info(f"📱 Telegram notification sent: {signal}")
        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")
    
    def send_daily_report(self, stats: dict):
        """Envoyer rapport journalier"""
        if not self.enabled:
            return
            
        message = f"""
📊 SWARNE DAILY REPORT

💰 Capital: ${stats.get('capital', 0):,.2f}
📈 Trades: {stats.get('trades', 0)}
✅ Win Rate: {stats.get('win_rate', 0):.1f}%
💵 P&L: ${stats.get('pnl', 0):+,.2f}

🐝 Active Bees: {stats.get('active_bees', 0)}
👑 Best Bee: {stats.get('best_bee', 'N/A')}
        """
        
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info("📱 Daily report sent")
        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")


class EmailNotifier:
    """Notificateur Email (à implémenter)"""
    pass
