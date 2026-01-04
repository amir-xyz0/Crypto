import telebot
import requests
import time
from datetime import datetime

# ========== تنظیمات اصلی ==========
TOKEN = "8245236522:AAHrwysDOzPBnzb4QdrTJ0L3n1P9U4PaIUM"
API_BASE = "https://api.coingecko.com/api/v3"
CACHE_TIMEOUT = 30

# ========== ساختارهای داده ==========
price_cache = {}
supported_coins = {
    'bitcoin': {'symbol': 'BTC', 'fa_name': 'بیت‌کوین'},
    'ethereum': {'symbol': 'ETH', 'fa_name': 'اتریوم'},
    'tether': {'symbol': 'USDT', 'fa_name': 'تتر'},
    'ripple': {'symbol': 'XRP', 'fa_name': 'ریپل'},
    'cardano': {'symbol': 'ADA', 'fa_name': 'کاردانو'},
    'solana': {'symbol': 'SOL', 'fa_name': 'سولانا'},
    'polkadot': {'symbol': 'DOT', 'fa_name': 'پولکادات'},
    'dogecoin': {'symbol': 'DOGE', 'fa_name': 'دوج کوین'},
    'chainlink': {'symbol': 'LINK', 'fa_name': 'چین لینک'},
    'litecoin': {'symbol': 'LTC', 'fa_name': 'لایت کوین'},
    'binancecoin': {'symbol': 'BNB', 'fa_name': 'بایننس کوین'},
    'avalanche': {'symbol': 'AVAX', 'fa_name': 'آوالانچ'},
    'stellar': {'symbol': 'XLM', 'fa_name': 'استلار'}
}

# ========== مقداردهی ربات ==========
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ========== توابع کمکی ==========
def get_price_data(coin_id):
    """دریافت اطلاعات قیمت از API با کشینگ"""
    current_time = time.time()
    
    if coin_id in price_cache:
        cached = price_cache[coin_id]
        if current_time - cached['time'] < CACHE_TIMEOUT:
            return cached['data']
    
    try:
        response = requests.get(
            f"{API_BASE}/simple/price",
            params={
                'ids': coin_id,
                'vs_currencies': 'usd,irr',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24h_vol': 'true'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                price_cache[coin_id] = {
                    'data': data[coin_id],
                    'time': current_time
                }
                return data[coin_id]
    except:
        pass
    
    return None

def format_currency(value):
    """فرمت‌دهی اعداد مالی"""
    try:
        if value >= 1000000000:
            return f"{value/1000000000:.2f} میلیارد"
        elif value >= 1000000:
            return f"{value/1000000:.2f} میلیون"
        elif value >= 1000:
            return f"{value/1000:.1f} هزار"
        return f"{value:.2f}"
    except:
        return "0"

def find_coin(query):
    """پیدا کردن کوین بر اساس ورودی کاربر"""
    query = query.lower().strip()
    
    if query in supported_coins:
        return query
    
    for coin_id, info in supported_coins.items():
        if query == info['symbol'].lower():
            return coin_id
        if query == info['fa_name'].lower():
            return coin_id
    
    for coin_id, info in supported_coins.items():
        if query in coin_id or query in info['fa_name'].lower():
            return coin_id
    
    return None

# ========== دستورات ربات ==========
@bot.message_handler(commands=['start'])
def handle_start(message):
    """راه‌اندازی ربات"""
    response = """
به ربات **قیمت ارزهای دیجیتال** خوش آمدید.

این ربات قیمت لحظه‌ای ارزهای دیجیتال را از منبع معتبر دریافت می‌کند.

روش استفاده:
نام ارز مورد نظر خود را تایپ کنید (مثال: bitcoin)
یا از دستورات زیر استفاده کنید:

دستورات موجود:
/list - نمایش لیست ارزهای پشتیبانی شده
/help - راهنمای استفاده
/info - اطلاعات ربات

برای شروع، نام یک ارز را وارد کنید.
"""
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['help'])
def handle_help(message):
    """راهنمای استفاده"""
    response = """
راهنمای استفاده از ربات:

1. برای دریافت قیمت یک ارز، نام آن را به انگلیسی یا فارسی تایپ کنید.
   مثال: bitcoin یا بیت‌کوین

2. می‌توانید از نماد ارزها نیز استفاده کنید.
   مثال: BTC یا ETH

3. برای مشاهده لیست کامل ارزها از دستور /list استفاده کنید.

4. اطلاعات فنی هر ارز شامل:
   - قیمت دلاری
   - قیمت تومانی
   - تغییرات 24 ساعته
   - حجم معاملات
   - ارزش بازار

منبع اطلاعات: CoinGecko API
"""
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['list'])
def handle_list(message):
    """نمایش لیست ارزها"""
    response = "ارزهای دیجیتال پشتیبانی شده:\n\n"
    
    for coin_id, info in supported_coins.items():
        response += f"{info['fa_name']} ({info['symbol']})\n"
        response += f"شناسه: {coin_id}\n\n"
    
    response += "برای دریافت قیمت، نام یا شناسه ارز را وارد کنید."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['info'])
def handle_info(message):
    """اطلاعات ربات"""
    response = """
اطلاعات ربات قیمت ارز دیجیتال

نسخه: 2.0
منبع داده: CoinGecko API
به‌روزرسانی: هر 30 ثانیه
تعداد ارزهای پشتیبانی شده: """ + str(len(supported_coins)) + """

ویژگی‌ها:
- قیمت لحظه‌ای به دلار و تومان
- تغییرات 24 ساعته
- حجم معاملات و ارزش بازار
- پشتیبانی از نام فارسی و انگلیسی
- کشینگ برای سرعت بیشتر

توسعه‌دهنده: امیرمهدی عزیزی 
"""
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """پردازش درخواست قیمت"""
    user_input = message.text.strip()
    
    coin_id = find_coin(user_input)
    
    if not coin_id:
        bot.reply_to(message, "ارز مورد نظر یافت نشد. لطفا نام صحیح ارز را وارد کنید یا از دستور /list برای مشاهده لیست استفاده کنید.")
        return
    
    coin_info = supported_coins[coin_id]
    price_data = get_price_data(coin_id)
    
    if not price_data:
        bot.reply_to(message, "در حال حاضر امکان دریافت قیمت وجود ندارد. لطفا چند لحظه دیگر تلاش کنید.")
        return
    
    usd_price = price_data.get('usd', 0)
    irr_price = price_data.get('irr', 0)
    change_24h = price_data.get('usd_24h_change', 0)
    market_cap = price_data.get('usd_market_cap', 0)
    volume_24h = price_data.get('usd_24h_vol', 0)
    
    change_status = "افزایش" if change_24h > 0 else "کاهش"
    change_color = "سبز" if change_24h > 0 else "قرمز"
    
    response = f"""
اطلاعات قیمت {coin_info['fa_name']} ({coin_info['symbol']})

قیمت فعلی:
{usd_price:,.2f} دلار
{irr_price:,.0f} تومان

تغییرات 24 ساعته:
{change_24h:+.2f}% ({change_status} - {change_color})

ارزش بازار:
{format_currency(market_cap)} دلار

حجم معاملات 24 ساعته:
{format_currency(volume_24h)} دلار

وضعیت: {'صعودی' if change_24h > 0 else 'نزولی'}

آخرین به‌روزرسانی: {datetime.now().strftime("%H:%M:%S")}

برای مشاهده ارز دیگر، نام آن را وارد کنید.
"""
    
    bot.reply_to(message, response)

# ========== اجرای ربات ==========
if __name__ == "__main__":
    bot.infinity_polling(timeout=20, long_polling_timeout=10)