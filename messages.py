from config import Config

class Messages:
    @staticmethod
    def welcome_message(user_name):
        return f"""
✨ **به {Config.BOT_NAME} خوش آمدید، {user_name}!** ✨

🏆 **سرمایه‌گذاری هوشمند، آینده‌ای روشن**
        
📊 *قیمت لحظه‌ای ارزهای دیجیتال*
💎 *هشدارهای هوشمند قیمتی*
📈 *تحلیل بازار و اخبار*
🔔 *اعلان‌های شخصی سازی شده*

🎯 **ویژگی‌های منحصربفرد ربات:**
✅ قیمت‌های واقعی از صرافی‌های معتبر
✅ اعلان فوری تغییرات قیمت
✅ اطلاعات کامل هر ارز دیجیتال
✅ رابط کاربری زیبا و ساده

📍 *برای شروع از منوی پایین استفاده کنید*
        """
    
    @staticmethod
    def main_menu():
        return "🏠 **منوی اصلی** - لطفا گزینه مورد نظر را انتخاب کنید:"
    
    @staticmethod
    def price_display(coin_name, price_data, vs_currency='usd'):
        price = price_data['price']
        change = price_data.get('change_24h', 0)
        
        # انتخاب ایموجی و رنگ بر اساس تغییرات
        if change > 0:
            trend = "📈"
            change_text = f"🟢 +{change:.2f}%"
        elif change < 0:
            trend = "📉"
            change_text = f"🔴 {change:.2f}%"
        else:
            trend = "📊"
            change_text = "⚪ 0.00%"
        
        return f"""
{trend} **{coin_name.upper()}**
        
💰 قیمت: **${price:,.2f}**
📊 تغییر 24h: {change_text}
🕐 آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}

💡 *برای اطلاعات بیشتر از منو استفاده کنید*
        """
    
    @staticmethod
    def coin_info(coin_data):
        name = coin_data.get('name', 'N/A')
        symbol = coin_data.get('symbol', '').upper()
        market_cap = coin_data.get('market_data', {}).get('market_cap', {}).get('usd', 0)
        volume = coin_data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
        description = coin_data.get('description', {}).get('en', 'No description available.')
        
        # کوتاه کردن توضیحات
        if len(description) > 500:
            description = description[:497] + "..."
        
        return f"""
🎯 **{name} ({symbol})**
        
📊 *مارکت کپ:* ${market_cap:,.0f}
💹 *حجم 24h:* ${volume:,.0f}
        
📝 **توضیحات:**
{description}

🔗 *وبسایت:* [{name}]({coin_data.get('links', {}).get('homepage', [''])[0]})
        """
    
    @staticmethod
    def dollar_alert(old_price, new_price, change_percent):
        direction = "افزایش" if new_price > old_price else "کاهش"
        
        return f"""
🚨 **هشدار قیمت دلار!** 🚨

💵 قیمت قبلی: {old_price:,.0f} ریال
💵 قیمت جدید: {new_price:,.0f} ریال
📊 تغییر: {change_percent:.2f}% {direction}

⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ *این هشدار به دلیل تغییر چشمگیر قیمت ارسال شده است*
        """
    
    @staticmethod
    def error_message():
        return "⚠️ **خطا در دریافت اطلاعات** - لطفا مجددا تلاش کنید."
    
    @staticmethod
    def type_warning():
        return "⚠️ **لطفا فقط از منو استفاده کنید!**\n\nبرای انتخاب ارز، لطفا از منوی 📋 لیست ارزها استفاده نمایید."
