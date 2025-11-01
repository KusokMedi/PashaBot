from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import shutil
import random

QUOTES_FILE = "quotes.json"
USERPICS_DIR = "userpics"

class QuoteManager:
    def __init__(self):
        self.quotes: List[Dict] = []
        # Создаем директорию для картинок если её нет
        os.makedirs(USERPICS_DIR, exist_ok=True)
        self.load_quotes()
    
    def load_quotes(self):
        """Загрузка цитат из файла"""
        if os.path.exists(QUOTES_FILE):
            try:
                with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
                    self.quotes = json.load(f)
            except:
                self.quotes = []
        else:
            self.quotes = []
    
    def save_quotes(self):
        """Сохранение цитат в файл"""
        with open(QUOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.quotes, f, ensure_ascii=False, indent=2)
    
    def save_user_pic(self, user_id: int, file_path: str) -> Optional[str]:
        """Сохранение картинки пользователя"""
        try:
            # Создаем имя файла
            ext = os.path.splitext(file_path)[1]
            new_path = os.path.join(USERPICS_DIR, f"user_{user_id}{ext}")
            
            # Копируем файл
            shutil.copy2(file_path, new_path)
            return new_path
        except Exception as e:
            print(f"Error saving user pic: {e}")
            return None
    
    def get_user_pic(self, user_id: int) -> Optional[str]:
        """Получение пути к картинке пользователя"""
        try:
            # Ищем файл пользователя
            for file in os.listdir(USERPICS_DIR):
                if file.startswith(f"user_{user_id}"):
                    return os.path.join(USERPICS_DIR, file)
            return None
        except:
            return None
    
    def add_quote(self, text: str, author: str = None, message_id: int = None, 
                 chat_id: int = None, user_id: int = None, user_pic: str = None) -> bool:
        """Добавление новой цитаты"""
        try:
            # Если передана картинка пользователя, сохраняем её
            saved_pic = None
            if user_pic and user_id:
                saved_pic = self.save_user_pic(user_id, user_pic)
            
            quote = {
                "text": text,
                "author": author,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message_id": message_id,
                "chat_id": chat_id,
                "user_id": user_id,
                "user_pic": saved_pic
            }
            self.quotes.append(quote)
            self.save_quotes()
            return True
        except Exception as e:
            print(f"Error adding quote: {e}")
            return False
    
    def get_random_quote(self) -> Optional[Dict]:
        """Получение случайной цитаты"""
        try:
            if not self.quotes:
                return None
            return random.choice(self.quotes)
        except Exception as e:
            print(f"Error getting random quote: {e}")
            return None
    
    def get_quote_by_message(self, message_id: int, chat_id: int) -> Optional[Dict]:
        """Поиск цитаты по ID сообщения"""
        try:
            for quote in self.quotes:
                if (quote.get('message_id') == message_id and 
                    quote.get('chat_id') == chat_id):
                    return quote
            return None
        except Exception as e:
            print(f"Error getting quote by message: {e}")
            return None
            
    def get_quotes_by_author(self, author: str) -> List[Dict]:
        """Получение всех цитат автора"""
        try:
            return [q for q in self.quotes if q.get('author') == author]
        except Exception as e:
            print(f"Error getting quotes by author: {e}")
            return []
            
    def get_quotes_count(self) -> int:
        """Получение количества цитат"""
        return len(self.quotes)