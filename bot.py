# در ابتدای فایل فقط این imports باشند:
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import requests
import time

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دیتابیس
db = Database()

class CoinYabBot:
    def __init__(self):
        self.api = APIClient()
        self.user_states = {}
    
    async def start(self, update: Update, context: CallbackContext):
        """دستور /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # ذخیره کاربر در دیتابیس
        db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # ارسال پیام خوش‌آمدگویی
        welcome_text = Messages.welcome_message(user.first_name)
        
        # ارسال پیام با فرمت‌بندی زیبا
        await update.message.reply_text(
            welcome_text,
            reply_markup=Keyboards.main_menu(),
            parse_mode='Markdown'
        )
        
        # ذخیره وضعیت کاربر
        self.user_states[chat_id] = {'state': 'main_menu'}
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """مدیریت پیام‌های متنی"""
        chat_id = update.effective_chat.id
        text = update.message.text
        
        # اگر کاربر تایپ کرد به جای استفاده از منو
        if text not in [
            "💰 قیمت لحظه‌ای", "📋 لیست ارزها", "💵 نرخ دلار",
            "🔔 تنظیم هشدار", "ℹ️ درباره ربات", "📊 اطلاعات ارز",
            "🏠 منوی اصلی", "◀️ صفحه قبل", "صفحه بعد ▶️",
            "📈 هشدار افزایش قیمت", "📉 هشدار کاهش قیمت",
            "🔕 غیرفعال کردن هشدار"
        ]:
            await update.message.reply_text(
                Messages.type_warning(),
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # پردازش انتخاب‌های منو
        if text == "💰 قیمت لحظه‌ای":
            await self.show_price_menu(update, context)
        
        elif text == "📋 لیست ارزها":
            await self.show_crypto_list(update, context)
        
        elif text == "💵 نرخ دلار":
            await self.show_dollar_rate(update, context)
        
        elif text == "🏠 منوی اصلی":
            await update.message.reply_text(
                Messages.main_menu(),
                reply_markup=Keyboards.main_menu()
            )
        
        elif text == "ℹ️ درباره ربات":
            await self.about_bot(update, context)
        
        elif text == "🔔 تنظیم هشدار":
            await update.message.reply_text(
                "⚙️ **تنظیمات هشدار**\n\nلطفا نوع هشدار مورد نظر را انتخاب کنید:",
                reply_markup=Keyboards.alert_settings()
            )
    
    async def show_price_menu(self, update: Update, context: CallbackContext):
        """نمایش منوی قیمت‌ها"""
        message = "🎯 **انتخاب ارز برای مشاهده قیمت**\n\n"
        message += "لطفا از لیست زیر یک ارز انتخاب کنید:\n\n"
        
        # نمایش 4 ارز محبوب
        popular_coins = ['bitcoin', 'ethereum', 'ripple', 'cardano']
        
        for coin_id in popular_coins:
            price_data = self.api.get_crypto_price(coin_id)
            if price_data['success']:
                coin_name = coin_id.capitalize()
                price = price_data['price']
                change = price_data['change_24h']
                
                change_emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                message += f"• {coin_name}: ${price:,.2f} {change_emoji}\n"
        
        message += "\nبرای مشاهده تمام ارزها، گزینه '📋 لیست ارزها' را انتخاب کنید."
        
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.crypto_list_page([])
        )
    
    async def show_crypto_list(self, update: Update, context: CallbackContext):
        """نمایش لیست ارزها"""
        coins_data = self.api.get_all_coins()
        
        if coins_data['success']:
            coins = coins_data['data'][:50]  # فقط 50 ارز اول
            context.user_data['crypto_list'] = coins
            context.user_data['current_page'] = 0
            
            await update.message.reply_text(
                "📊 **لیست ارزهای دیجیتال**\n\nلطفا ارز مورد نظر را انتخاب کنید:",
                reply_markup=Keyboards.crypto_list_page(coins, page=0)
            )
        else:
            await update.message.reply_text(
                Messages.error_message(),
                reply_markup=Keyboards.main_menu()
            )
    
    async def show_dollar_rate(self, update: Update, context: CallbackContext):
        """نمایش نرخ دلار"""
        rate_data = self.api.get_dollar_rate()
        
        if rate_data['success']:
            price = rate_data['price']
            change = rate_data['change']
            
            if change > 0:
                trend = "📈 افزایش"
                emoji = "🟢"
            elif change < 0:
                trend = "📉 کاهش"
                emoji = "🔴"
            else:
                trend = "📊 ثابت"
                emoji = "⚪"
            
            message = f"""
💵 **نرخ لحظه‌ای دلار**
            
💰 قیمت: **{price:,.0f} ریال**
📊 وضعیت: {emoji} {trend}
⏰ زمان: {datetime.now().strftime('%H:%M:%S')}
            
💡 *منبع: صرافی‌های معتبر ایرانی*
            """
            
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.main_menu(),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                Messages.error_message(),
                reply_markup=Keyboards.main_menu()
            )
    
    async def about_bot(self, update: Update, context: CallbackContext):
        """درباره ربات"""
        message = f"""
🤖 **{Config.BOT_NAME}**
        
📱 **یک ربات هوشمند برای پیگیری بازار ارزهای دیجیتال**
        
✨ **ویژگی‌ها:**
✅ قیمت لحظه‌ای ارزهای دیجیتال
✅ هشدار هوشمند تغییرات قیمت
✅ اطلاعات کامل هر ارز
✅ رابط کاربری زیبا و ساده
✅ به‌روزرسانی خودکار
        
🔧 **تکنولوژی:**
• Python 3.11+
• python-telegram-bot
• CoinGecko API
• SQLite Database
        
👨‍💻 **توسعه‌دهنده:** {Config.DEVELOPER}
📅 **ورژن:** 1.0.0
        
💡 *برای استفاده بهینه، حتما نوتیفیکیشن را فعال کنید*
        """
        
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.main_menu(),
            parse_mode='Markdown'
        )
    
    async def send_price_alerts(self, context: CallbackContext):
        """ارسال هشدارهای قیمتی"""
        alerts = db.get_all_active_alerts()
        
        for alert in alerts:
            user_id, coin_id, alert_type, threshold = alert[1:5]
            
            # دریافت قیمت فعلی
            price_data = self.api.get_crypto_price(coin_id)
            
            if price_data['success']:
                # بررسی شرایط هشدار
                # (این بخش نیاز به توسعه دارد)
                pass

def main():
    """تابع اصلی اجرای ربات"""
    
    # ایجاد اپلیکیشن
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # ایجاد نمونه ربات
    bot = CoinYabBot()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # اضافه کردن job برای به‌روزرسانی‌های دوره‌ای
    job_queue = application.job_queue
    job_queue.run_repeating(bot.send_price_alerts, interval=Config.PRICE_UPDATE_INTERVAL, first=10)
    
    # اجرای ربات
    logger.info("ربات Coin Yab در حال اجرا است...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
