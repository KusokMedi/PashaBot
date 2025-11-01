from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import random
from typing import Tuple, Optional

class QuoteImage:
    def __init__(self):
        # Настройка путей к ресурсам
        self.resources_dir = "resources"
        self.backgrounds_dir = os.path.join(self.resources_dir, "backgrounds")
        
        # Пути к файлам шрифтов
        self.quote_font = "C:\\Windows\\Fonts\\Gabriola.ttf"  # Красивый шрифт для цитат
        self.author_font = "C:\\Windows\\Fonts\\georgiab.ttf"  # Georgia Bold для автора
        self.default_background = os.path.join(self.backgrounds_dir, "quote_bg.jpg")
        

    

    


    def create_quote_image(self, text: str, author: Optional[str] = None, user_id: Optional[int] = None, 
                      user_pic_path: Optional[str] = None) -> Optional[str]:
        """Создание изображения с цитатой"""
        try:
            # Загружаем фон из resources
            if not os.path.exists(self.default_background):
                print("Ошибка: фоновое изображение не найдено")
                return None
                
            img = Image.open(self.default_background)
            draw = ImageDraw.Draw(img)
            
            # Получаем размеры изображения
            img_w, img_h = img.size
            padding = 80  # Увеличиваем отступы для лучшего внешнего вида
            max_text_width = img_w - (padding * 2)
            
            # Настраиваем шрифты для цитаты и автора
            quote_font_size = 60  # Уменьшаем размер шрифта
            quote_font = ImageFont.truetype(self.quote_font, quote_font_size)
            author_font = ImageFont.truetype(self.author_font, 32)
            
            # Подготавливаем текст цитаты с учётом ширины изображения
            max_width = int(img_w * 0.8)  # Используем 80% ширины изображения
            lines = []
            words = text.split()
            current_line = []
            
            for word in words:
                current_line.append(word)
                line = ' '.join(current_line)
                bbox = quote_font.getbbox(line)
                if bbox[2] - bbox[0] > max_width:
                    if len(current_line) == 1:
                        lines.append(line)
                        current_line = []
                    else:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
                
            quote_text = '\n'.join(lines)
            quote_bbox = quote_font.getbbox(quote_text)
            quote_w = quote_bbox[2] - quote_bbox[0]
            quote_h = quote_bbox[3] - quote_bbox[1]
            
            # Позиционируем текст цитаты по центру, но выше если есть аватар
            quote_x = (img_w - quote_w) // 2
            if user_pic_path:
                quote_y = (img_h - quote_h) // 2 - 60  # Ещё выше если есть аватар
            else:
                quote_y = (img_h - quote_h) // 2 - 30
            
            # Рисуем основной текст цитаты
            text_color = (40, 40, 40)  # Почти чёрный цвет для текста
            quote_shadow_offset = 2
            
            # Добавляем лёгкую тень для текста
            draw.text((quote_x + quote_shadow_offset, quote_y + quote_shadow_offset), 
                     quote_text, font=quote_font, fill=(200, 200, 200))  # Тень
            draw.text((quote_x, quote_y), quote_text, 
                     font=quote_font, fill=text_color)  # Основной текст
            
            # Если есть аватар пользователя, добавляем его
            if user_pic_path and os.path.exists(user_pic_path):
                try:
                    # Загружаем и масштабируем аватар
                    avatar = Image.open(user_pic_path)
                    avatar_size = 100  # Увеличиваем размер аватара
                    avatar = avatar.resize((avatar_size, avatar_size))
                    
                    # Создаем круглую маску с белой границей
                    mask_size = avatar_size + 8  # Добавляем место для границы
                    mask = Image.new('L', (mask_size, mask_size), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    
                    # Рисуем белую границу
                    mask_draw.ellipse((0, 0, mask_size-1, mask_size-1), fill=255)
                    
                    # Создаем финальное изображение с аватаром
                    avatar_with_border = Image.new('RGBA', (mask_size, mask_size), (255, 255, 255, 0))
                    avatar_with_border.paste(avatar, (4, 4))  # Центрируем аватар внутри границы
                    
                    # Позиционируем аватар в правом нижнем углу
                    avatar_x = img_w - mask_size - 30
                    avatar_y = img_h - mask_size - 30
                    
                    # Накладываем аватар с маской
                    img.paste(avatar_with_border, (avatar_x, avatar_y), mask)
                except Exception as e:
                    print(f"Ошибка при добавлении аватара: {e}")
            
            # Если есть автор, добавляем его имя
            if author:
                author_text = f"— {author}"
                author_bbox = author_font.getbbox(author_text)
                author_w = author_bbox[2] - author_bbox[0]
                
                # Позиционируем имя автора
                author_x = (img_w - author_w) // 2
                author_y = quote_y + quote_h + 50
                
                # Добавляем тень для имени автора
                draw.text((author_x + quote_shadow_offset, author_y + quote_shadow_offset), 
                         author_text, font=author_font, fill=(200, 200, 200))
                draw.text((author_x, author_y), author_text, 
                         font=author_font, fill=text_color)
            
            # Сохраняем изображение во временный файл
            output_path = "temp_quote.png"
            img.save(output_path, format='PNG', quality=95)
            return output_path
        except Exception as e:
            print(f"Ошибка при создании изображения: {e}")
            return None