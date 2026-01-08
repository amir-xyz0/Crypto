import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name='coin_yab.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # جدول کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP,
                alert_settings TEXT DEFAULT '{}'
            )
        ''')
        
        # جدول هشدارها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                coin_id TEXT,
                alert_type TEXT,
                threshold REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name, last_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, join_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, datetime.now()))
        self.conn.commit()
    
    def get_user_alerts(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM alerts 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        return cursor.fetchall()
    
    def add_alert(self, user_id, coin_id, alert_type, threshold):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts 
            (user_id, coin_id, alert_type, threshold, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, coin_id, alert_type, threshold, datetime.now()))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_active_alerts(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alerts WHERE is_active = 1')
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()
