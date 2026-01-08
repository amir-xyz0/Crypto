import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # تلگرام
    TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
    # APIها
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
    ALPHA_VANTAGE_API = "https://www.alphavantage.co/query"
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo')  # کلید رایگان بگیرید
    
    # تنظیمات ربات
    PRICE_UPDATE_INTERVAL = 60  # ثانیه
    ALERT_THRESHOLD = 2  # درصد تغییر برای هشدار
    SUPPORTED_COINS = [
        'bitcoin', 'ethereum', 'ripple', 'cardano', 
        'solana', 'polkadot', 'dogecoin', 'tether'
    ]
    
    # متن‌ها
    BOT_NAME = "Coin Yab 🪙"
    DEVELOPER = "امیرمهدی عزیزی"
