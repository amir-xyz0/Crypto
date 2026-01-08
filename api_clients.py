import requests
import json
from datetime import datetime
from config import Config

class APIClient:
    @staticmethod
    def get_crypto_price(coin_id='bitcoin', vs_currency='usd'):
        """دریافت قیمت ارز دیجیتال از CoinGecko"""
        try:
            url = f"{Config.COINGECKO_API}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': vs_currency,
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                return {
                    'price': data[coin_id].get(vs_currency, 0),
                    'change_24h': data[coin_id].get(f'{vs_currency}_24h_change', 0),
                    'success': True
                }
            return {'success': False, 'error': 'Coin not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_all_coins():
        """دریافت لیست تمام ارزها"""
        try:
            url = f"{Config.COINGECKO_API}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 100,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_dollar_rate():
        """نرخ دلار به ریال"""
        try:
            # استفاده از API رایگان نرخ ارز
            url = "https://api.tgju.online/v1/data/sana/price_dollar_rl"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK':
                price = float(data['data']['price'])
                change = float(data['data']['change'])
                return {
                    'price': price,
                    'change': change,
                    'success': True
                }
            
            # Fallback به API دیگر
            url = "https://api.dollar-api.ir/v1/current"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return {
                'price': data.get('price', 0),
                'change': 0,
                'success': True
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_coin_info(coin_id):
        """دریافت اطلاعات کامل یک ارز"""
        try:
            url = f"{Config.COINGECKO_API}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
