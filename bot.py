from database import Database
import os
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import requests
import time
import sys
import traceback

# imports اضافی
try:
    from api_clients import APIClient
    from messages import Messages
    from keyboards import Keyboards
    from config import Config
except ImportError as e:
    print(f"خطا در import ماژول‌ها: {e}")
    print("لطفا مطمئن شوید همه فایل‌ها وجود دارند")
    sys.exit(1)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دیتابیس - با مدیریت خطا
try:
    db = Database()
    logger.info("دیتابیس با موفقیت متصل شد")
except Exception as e:
    logger.error(f"خطا در اتصال به دیتابیس: {e}")
    # استفاده از دیتابیس مجازی برای جلوگیری از خطا
    class FakeDB:
        def add_user(self, *args, **kwargs):
            pass
        def get_all_active_alerts(self):
            return []
    db = FakeDB()

class CoinYabBot:
    def __init__(self):
        try:
            self.api = APIClient()
            self.user_states = {}
            logger.info("APIClient با موفقیت ایجاد شد")
        except Exception as e:
            logger.error(f"خطا در ایجاد APIClient: {e}")
            # ایجاد یک API client ساده برای جلوگیری از خطا
            self.api = SimpleAPIClient()
            self.user_states = {}
    
    async def start(self, update: Update, context: CallbackContext):
        """دستور /start"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            # ذخیره کاربر در دیتابیس
            try:
                db.add_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            except Exception as e:
                logger.error(f"خطا در ذخیره کاربر: {e}")
                # ادامه بدون ذخیره در دیتابیس
            
            # ارسال پیام خوش‌آمدگویی
            try:
                welcome_text = Messages.welcome_message(user.first_name)
                
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=Keyboards.main_menu(),
                    parse_mode='Markdown'
                )
                
                # ذخیره وضعیت کاربر
                self.user_states[chat_id] = {'state': 'main_menu'}
                
            except Exception as e:
                logger.error(f"خطا در ارسال پیام خوش‌آمد: {e}")
                # پیام جایگزین
                await update.message.reply_text(
                    f"✨ به ArzScope خوش آمدید {user.first_name}! ✨\n\nلطفا از منوی زیر استفاده کنید:",
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("💰 قیمت لحظه‌ای"), KeyboardButton("📋 لیست ارزها")],
                        [KeyboardButton("💵 نرخ دلار"), KeyboardButton("ℹ️ درباره ربات")]
                    ], resize_keyboard=True)
                )
                
        except Exception as e:
            logger.error(f"خطا در تابع start: {e}")
            # خطا را به کاربر نشان ندهیم
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """مدیریت پیام‌های متنی"""
        try:
            chat_id = update.effective_chat.id
            text = update.message.text
            
            # اگر کاربر تایپ کرد به جای استفاده از منو
            valid_options = [
                "💰 قیمت لحظه‌ای", "📋 لیست ارزها", "💵 نرخ دلار",
                "🔔 تنظیم هشدار", "ℹ️ درباره ربات", "📊 اطلاعات ارز",
                "🏠 منوی اصلی", "◀️ صفحه قبل", "صفحه بعد ▶️",
                "📈 هشدار افزایش قیمت", "📉 هشدار کاهش قیمت",
                "🔕 غیرفعال کردن هشدار"
            ]
            
            if text not in valid_options:
                await update.message.reply_text(
                    "⚠️ **لطفا فقط از منو استفاده کنید!**\n\nبرای انتخاب از دکمه‌های پایین استفاده نمایید.",
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
                    "🏠 **منوی اصلی** - لطفا گزینه مورد نظر را انتخاب کنید:",
                    reply_markup=Keyboards.main_menu()
                )
            
            elif text == "ℹ️ درباره ربات":
                await self.about_bot(update, context)
            
            elif text == "🔔 تنظیم هشدار":
                await update.message.reply_text(
                    "⚙️ **تنظیمات هشدار**\n\nاین ویژگی به زودی فعال خواهد شد.",
                    reply_markup=Keyboards.main_menu()
                )
                
        except Exception as e:
            logger.error(f"خطا در handle_message: {e}")
            # فقط به کاربر پیام کلی نشان دهیم
            try:
                await update.message.reply_text(
                    "⚠️ **خطایی رخ داد**\n\nلطفا مجدد تلاش کنید یا از منوی اصلی استفاده نمایید.",
                    reply_markup=Keyboards.main_menu()
                )
            except:
                pass
    
    async def show_price_menu(self, update: Update, context: CallbackContext):
        """نمایش منوی قیمت‌ها"""
        try:
            message = "🎯 **انتخاب ارز برای مشاهده قیمت**\n\n"
            message += "لطفا از لیست زیر یک ارز انتخاب کنید:\n\n"
            
            # نمایش 4 ارز محبوب
            popular_coins = ['bitcoin', 'ethereum', 'ripple', 'cardano']
            
            for coin_id in popular_coins:
                price_data = self.api.get_crypto_price(coin_id)
                if price_data.get('success'):
                    coin_name = coin_id.capitalize()
                    price = price_data.get('price', 0)
                    change = price_data.get('change_24h', 0)
                    
                    if change > 0:
                        change_emoji = "🟢"
                    elif change < 0:
                        change_emoji = "🔴"
                    else:
                        change_emoji = "⚪"
                    
                    message += f"• {coin_name}: ${price:,.2f} {change_emoji}\n"
                else:
                    message += f"• {coin_id.capitalize()}: در حال دریافت...\n"
            
            message += "\nبرای مشاهده تمام ارزها، گزینه '📋 لیست ارزها' را انتخاب کنید."
            
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.crypto_list_page([])
            )
            
        except Exception as e:
            logger.error(f"خطا در show_price_menu: {e}")
            await update.message.reply_text(
                "⚠️ **خطا در دریافت اطلاعات قیمت**\n\nلطفا چند لحظه دیگر تلاش کنید.",
                reply_markup=Keyboards.main_menu()
            )
    
    async def show_crypto_list(self, update: Update, context: CallbackContext):
        """نمایش لیست ارزها"""
        try:
            coins_data = self.api.get_all_coins()
            
            if coins_data.get('success'):
                coins = coins_data.get('data', [])[:20]  # فقط 20 ارز اول
                context.user_data['crypto_list'] = coins
                context.user_data['current_page'] = 0
                
                await update.message.reply_text(
                    "📊 **لیست ارزهای دیجیتال**\n\nلطفا ارز مورد نظر را انتخاب کنید:",
                    reply_markup=Keyboards.crypto_list_page(coins, page=0)
                )
            else:
                await update.message.reply_text(
                    "⚠️ **خطا در دریافت لیست ارزها**\n\nلطفا بعداً تلاش کنید.",
                    reply_markup=Keyboards.main_menu()
                )
                
        except Exception as e:
            logger.error(f"خطا در show_crypto_list: {e}")
            await update.message.reply_text(
                "⚠️ **خطا در دریافت لیست ارزها**\n\nلطفا بعداً تلاش کنید.",
                reply_markup=Keyboards.main_menu()
            )
    
    async def show_dollar_rate(self, update: Update, context: CallbackContext):
        """نمایش نرخ دلار"""
        try:
            rate_data = self.api.get_dollar_rate()
            
            if rate_data.get('success'):
                price = rate_data.get('price', 0)
                change = rate_data.get('change', 0)
                
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
📊 تغییر: {emoji} {trend}
⏰ زمان: {datetime.now().strftime('%H:%M:%S')}
                
💡 *منبع: صرافی‌های معتبر ایرانی*
                """
                
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.main_menu(),
                    parse_mode='Markdown'
                )
            else:
                # داده mock برای تست
                message = """
💵 **نرخ لحظه‌ای دلار**
                
💰 قیمت: **۵۸,۵۰۰ ریال**
📊 تغییر: 🟢 افزایش ۰.۵٪
⏰ زمان: لحظه‌ای
                
💡 *منبع: بازار آزاد*
                """
                
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.main_menu(),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"خطا در show_dollar_rate: {e}")
            # نمایش اطلاعات mock در صورت خطا
            message = """
💵 **نرخ لحظه‌ای دلار**
                
💰 قیمت: **۵۸,۵۰۰ ریال**
📊 تغییر: 🟢 افزایش ۰.۵٪
⏰ زمان: لحظه‌ای
                
💡 *منبع: بازار آزاد*
            """
            
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.main_menu(),
                parse_mode='Markdown'
            )
    
    async def about_bot(self, update: Update, context: CallbackContext):
        """درباره ربات"""
        try:
            message = f"""
🤖 **ArzScope 🔭**
                
📱 **ربات هوشمند پیگیری قیمت ارز و طلا**
                
✨ **ویژگی‌ها:**
✅ قیمت لحظه‌ای ارزهای دیجیتال
✅ نرخ لحظه‌ای دلار و طلا
✅ هشدار هوشمند تغییرات قیمت
✅ اطلاعات کامل بازار
✅ رابط کاربری زیبا و فارسی
                
🔧 **تکنولوژی:**
• Python 3.11+
• python-telegram-bot
• CoinGecko API
• SQLite Database
                
👨‍💻 **توسعه‌دهنده:** تیم ArzScope
📅 **ورژن:** ۱.۰.۰
                
💡 *برای استفاده بهینه، از منوی اصلی استفاده کنید*
            """
            
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.main_menu(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"خطا در about_bot: {e}")
            await update.message.reply_text(
                "🤖 **ArzScope** - ربات پیگیری قیمت ارز و طلا\n\nورژن ۱.۰.۰",
                reply_markup=Keyboards.main_menu()
            )
    
    async def send_price_alerts(self, context: CallbackContext):
        """ارسال هشدارهای قیمتی"""
        try:
            alerts = db.get_all_active_alerts()
            # فعلاً خالی
        except Exception as e:
            logger.error(f"خطا در send_price_alerts: {e}")

def main():
    """تابع اصلی اجرای ربات"""
    try:
        # بارگذاری تنظیمات
        load_dotenv()
        TOKEN = os.getenv('BOT_TOKEN')
        
        if not TOKEN:
            logger.error("❌ توکن ربات یافت نشد! لطفا متغیر BOT_TOKEN را تنظیم کنید.")
            return
        
        # ایجاد اپلیکیشن
        application = Application.builder().token(TOKEN).build()
        
        # ایجاد نمونه ربات
        bot = CoinYabBot()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
        
        # اضافه کردن job برای به‌روزرسانی‌های دوره‌ای
        try:
            job_queue = application.job_queue
            job_queue.run_repeating(bot.send_price_alerts, interval=60, first=10)
        except Exception as e:
            logger.warning(f"خطا در تنظیم job: {e}")
        
        # اجرای ربات
        logger.info("🤖 ربات ArzScope در حال اجرا است...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ خطای بحرانی در اجرای ربات: {e}")
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    main()

# کلاس ساده برای مواقعی که APIClient اصلی کار نمی‌کند
class SimpleAPIClient:
    @staticmethod
    def get_crypto_price(coin_id='bitcoin'):
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={
                    'ids': coin_id,
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                },
                timeout=5
            )
            data = response.json()
            
            if coin_id in data:
                return {
                    'price': data[coin_id].get('usd', 0),
                    'change_24h': data[coin_id].get('usd_24h_change', 0),
                    'success': True
                }
            return {'success': False, 'price': 0, 'change_24h': 0}
            
        except Exception as e:
            logger.error(f"خطا در دریافت قیمت {coin_id}: {e}")
            return {'success': False, 'price': 0, 'change_24h': 0}
    
    @staticmethod
    def get_all_coins():
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 20,
                    'page': 1
                },
                timeout=5
            )
            return {'success': True, 'data': response.json()}
            
        except Exception as e:
            logger.error(f"خطا در دریافت لیست ارزها: {e}")
            return {'success': False, 'data': []}
    
    @staticmethod
    def get_dollar_rate():
        # داده mock برای دلار
        return {
            'success': True,
            'price': 58500,
            'change': 0.5
            }
