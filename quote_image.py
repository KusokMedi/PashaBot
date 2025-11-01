from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from typing import Tuple

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
        lines = []
        max_line_width = 0
        
        # Делим текст на строки по ширине
        for line in textwrap.wrap(text, width=width):
            line_width = font.getlength(line)
            max_line_width = max(max_line_width, line_width)
            lines.append(line)
            
        return '\n'.join(lines), len(lines)
    
    def create_quote_image(self, text: str, author: str = None) -> str:
        """Создание изображения с цитатой"""
        try:
            # Загружаем фон
            img = Image.open(self.default_background)
            draw = ImageDraw.Draw(img)
            
            # Настраиваем размер шрифта
            font_size = 40
            font = ImageFont.truetype(self.default_font, font_size)
            
            # Получаем размеры изображения
            img_w, img_h = img.size
            
            # Подготавливаем текст
            max_chars = 40
            quote_text, num_lines = self._wrap_text(text, max_chars, font)
            
            # Вычисляем позиции для текста
            text_bbox = draw.textbbox((0, 0), quote_text, font=font)
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