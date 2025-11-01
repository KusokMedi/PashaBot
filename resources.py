import os
import requests
from typing import Optional

def download_file(url: str, save_path: str) -> bool:
    """Скачивание файла по URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Создаем директорию если её нет
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Сохраняем файл
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def get_user_avatar(user_id: int, save_dir: str) -> Optional[str]:
    """Получение и сохранение аватара пользователя"""
    try:
        # Создаем путь для сохранения
        avatar_path = os.path.join(save_dir, f"avatar_{user_id}.jpg")
        
        # Если аватар уже скачан - возвращаем путь
        if os.path.exists(avatar_path):
            return avatar_path
            
        # Получаем фотографии пользователя через Telegram API
        api_url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/getUserProfilePhotos"
        response = requests.get(api_url, params={'user_id': user_id, 'limit': 1})
        response.raise_for_status()
        
        data = response.json()
        if data['ok'] and data['result']['total_count'] > 0:
            # Получаем информацию о фото
            photo = data['result']['photos'][0][-1]  # Берем последнюю (самую большую) версию
            file_id = photo['file_id']
            
            # Получаем путь к файлу
            file_path_url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/getFile"
            response = requests.get(file_path_url, params={'file_id': file_id})
            response.raise_for_status()
            
            file_path = response.json()['result']['file_path']
            
            # Скачиваем файл
            download_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file_path}"
            if download_file(download_url, avatar_path):
                return avatar_path
                
        return None
    except Exception as e:
        print(f"Error getting user avatar: {e}")
        return None

# URL красивых шрифтов
FONTS = {
    'regular': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf',
    'bold': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf',
    'italic': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Italic.ttf'
}