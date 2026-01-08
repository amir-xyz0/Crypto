from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

class Keyboards:
    @staticmethod
    def main_menu():
        """منوی اصلی"""
        keyboard = [
            [KeyboardButton("💰 قیمت لحظه‌ای"), KeyboardButton("📋 لیست ارزها")],
            [KeyboardButton("💵 نرخ دلار"), KeyboardButton("🔔 تنظیم هشدار")],
            [KeyboardButton("ℹ️ درباره ربات"), KeyboardButton("📊 اطلاعات ارز")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def crypto_list_page(coins, page=0, items_per_page=8):
        """لیست ارزها با صفحه‌بندی"""
        keyboard = []
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        
        for i in range(start_idx, min(end_idx, len(coins))):
            coin = coins[i]
            name = coin['name'][:20]  # محدود کردن طول نام
            keyboard.append([KeyboardButton(f"{name} ({coin['symbol'].upper()})")])
        
        # دکمه‌های صفحه‌بندی
        nav_buttons = []
        if page > 0:
            nav_buttons.append(KeyboardButton("◀️ صفحه قبل"))
        if end_idx < len(coins):
            nav_buttons.append(KeyboardButton("صفحه بعد ▶️"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([KeyboardButton("🏠 منوی اصلی")])
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def alert_settings():
        """تنظیمات هشدار"""
        keyboard = [
            [KeyboardButton("📈 هشدار افزایش قیمت"), KeyboardButton("📉 هشدار کاهش قیمت")],
            [KeyboardButton("🔕 غیرفعال کردن هشدار"), KeyboardButton("🏠 منوی اصلی")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def back_to_main():
        """دکمه بازگشت به منو"""
        return ReplyKeyboardMarkup([[KeyboardButton("🏠 منوی اصلی")]], resize_keyboard=True)
