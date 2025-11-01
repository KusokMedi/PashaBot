from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from typing import Tuple, Optional

class QuoteImage:
    def __init__(self):
        # Настройка путей к ресурсам
        self.resources_dir = "resources"
        self.fonts_dir = os.path.join(self.resources_dir, "fonts")
        self.backgrounds_dir = os.path.join(self.resources_dir, "backgrounds")
        
        # Создаем директории если их нет
        os.makedirs(self.fonts_dir, exist_ok=True)
        os.makedirs(self.backgrounds_dir, exist_ok=True)
        
        # Пути к файлам по умолчанию
        self.default_font = os.path.join(self.fonts_dir, "Roboto-Regular.ttf")
        self.default_background = os.path.join(self.backgrounds_dir, "quote_bg.jpg")
        
        # Создаем стандартный фон если его нет
        if not os.path.exists(self.default_background):
            self._create_default_background()
            
        # Проверяем наличие шрифта
        if not os.path.exists(self.default_font):
            # Используем системный шрифт если нашего нет
            system_fonts = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            for font in system_fonts:
                if os.path.exists(font):
                    self.default_font = font
                    break
    
    def _create_default_background(self):
        """Создание стандартного фона для цитат"""
        img = Image.new('RGB', (800, 400), color='#2f3136')
        img.save(self.default_background)
    
    def _wrap_text(self, text: str, width: int, font: ImageFont.FreeTypeFont) -> Tuple[str, int]:
        """Перенос длинного текста на новые строки"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line = ' '.join(current_line)
            # Проверяем ширину текущей строки
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            
            # Если строка стала слишком длинной
            if line_width > width:
                if len(current_line) == 1:
                    # Если одно слово слишком длинное, оставляем его
                    lines.append(line)
                    current_line = []
                else:
                    # Убираем последнее слово и добавляем строку
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
        
        # Добавляем последнюю строку
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines), len(lines)
    
    def _calculate_optimal_font_size(self, text: str, max_width: int, max_height: int, 
                                  start_size: int = 40, min_size: int = 16) -> tuple[int, ImageFont.FreeTypeFont, str, int]:
        """Вычисляет оптимальный размер шрифта для текста"""
        font_size = start_size
        while font_size >= min_size:
            font = ImageFont.truetype(self.default_font, font_size)
            # Пробуем разные значения для переноса слов
            for max_chars in range(40, 20, -5):
                wrapped_text, num_lines = self._wrap_text(text, max_chars, font)
                bbox = font.getbbox(wrapped_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1] * num_lines
                
                # Проверяем, помещается ли текст
                if text_width <= max_width and text_height <= max_height:
                    return font_size, font, wrapped_text, num_lines
            
            font_size -= 2
        
        # Если дошли до минимального размера, возвращаем его
        font = ImageFont.truetype(self.default_font, min_size)
        wrapped_text, num_lines = self._wrap_text(text, 40, font)
        return min_size, font, wrapped_text, num_lines

    def create_quote_image(self, text: str, author: Optional[str] = None, user_id: Optional[int] = None, user_pic_path: Optional[str] = None) -> Optional[str]:
        """Создание изображения с цитатой"""
        try:
            # Загружаем фон
            img = Image.open(self.default_background)
            draw = ImageDraw.Draw(img)
            
            # Получаем размеры изображения и области для текста
            img_w, img_h = img.size
            padding = 40
            margin = 60
            max_text_width = img_w - (padding * 2 + margin * 2)
            max_text_height = img_h - (padding * 2 + margin)
            
            # Вычисляем оптимальный размер шрифта и подготавливаем текст
            font_size, font, quote_text, num_lines = self._calculate_optimal_font_size(
                text, max_text_width, max_text_height
            )
            
            # Получаем размеры текста
            text_bbox = font.getbbox(quote_text)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            # Центрируем текст
            x = (img_w - text_w) // 2
            y = (img_h - text_h) // 2 - 20  # Немного выше центра
            
            # Рисуем текст
            draw.text((x, y), quote_text, font=font, fill='white')
            
            # Добавляем автора если есть
            if author:
                author_font = ImageFont.truetype(self.default_font, font_size // 2)
                author_text = f"— {author}"
                author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
                author_w = author_bbox[2] - author_bbox[0]
                
                # Размещаем автора внизу справа
                author_x = img_w - author_w - 20
                author_y = img_h - 40
                
                draw.text((author_x, author_y), author_text, font=author_font, fill='#cccccc')
            
            # Сохраняем результат
            output_path = "temp_quote.png"
            img.save(output_path)
            return output_path
            
        except Exception as e:
            print(f"Error creating quote image: {e}")
            return None