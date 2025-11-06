from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import random
import os
from lines import *  # Импортируем все сообщения
from typing import Optional
from quotes import QuoteManager
from quote_image import QuoteImage

def register_handlers(bot: TeleBot):
    # Инициализация менеджеров
    quote_manager = QuoteManager()
    quote_image = QuoteImage()
    
    # Команда /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(BTN_TTS), KeyboardButton(BTN_QUOTES))
        keyboard.add(KeyboardButton(BTN_RANDOM), KeyboardButton(BTN_DAILY))
        keyboard.add(KeyboardButton(BTN_HELP))
        
        bot.reply_to(message, MSG_START, reply_markup=keyboard)

    # Команда /help
    @bot.message_handler(commands=['help'])
    def cmd_help(message: Message):
        bot.reply_to(message, MSG_HELP)
    from gtts import gTTS
    import os
    import tempfile
    
    # Хранение выбранного языка для пользователей
    user_langs = {}  # TODO: Заменить на базу данных
    
    # Функция для создания голосового сообщения
    def create_voice_message(text: str, lang: str = 'ru') -> Optional[str]:
        temp_file = None
        try:
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            # Генерируем голосовое сообщение
            tts = gTTS(text=text, lang=lang)
            # Сохраняем во временный файл
            tts.save(temp_file.name)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"TTS Error: {e}")
            if temp_file:
                try:
                    temp_file.close()
                    os.unlink(temp_file.name)
                except:
                    pass
            return None
    
    # Команда TTS
    @bot.message_handler(commands=['tts'])
    def cmd_tts(message: Message):
        if not message or not message.from_user or not message.text:
            return
            
        command_args = message.text.split(maxsplit=1)
        if len(command_args) > 1:
            # Если текст указан сразу после команды
            process_tts_text(message, command_args[1])
        else:
            # Создаем клавиатуру с кнопкой отмены
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(BTN_CANCEL))
                
            # Просим пользователя ввести текст для озвучки
            msg = bot.reply_to(message, MSG_TTS_PROMPT, reply_markup=keyboard)
            # Регистрируем следующий шаг
            bot.register_next_step_handler(msg, lambda m: process_tts_text(m))
        
    def process_tts_text(message: Message, direct_text: Optional[str] = None):
        if not message or not message.text or not message.from_user:
            return
            
        # Если текст передан напрямую или получен из сообщения
        text = direct_text if direct_text else message.text
            
        # Если пользователь нажал "Отмена" и текст не был передан напрямую
        if not direct_text and text == BTN_CANCEL:
            # Возвращаем основную клавиатуру
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(BTN_TTS), KeyboardButton(BTN_QUOTES))
            keyboard.add(KeyboardButton(BTN_RANDOM), KeyboardButton(BTN_DAILY))
            keyboard.add(KeyboardButton(BTN_HELP))
            bot.reply_to(message, MSG_CANCELLED, reply_markup=keyboard)
            return        # Проверка длины текста
        if len(text) > 1000:
            bot.reply_to(message, MSG_TTS_TOO_LONG)
            return
            
        # Получаем выбранный язык пользователя или используем русский по умолчанию
        lang_code, _ = TTS_LANGS.get(
            user_langs.get(message.from_user.id, 1),  # 1 = русский по умолчанию
            ('ru', '🇷🇺 Русский')
        )
        
        # Возвращаем основную клавиатуру
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(BTN_TTS), KeyboardButton(BTN_QUOTES))
        keyboard.add(KeyboardButton(BTN_RANDOM), KeyboardButton(BTN_DAILY))
        keyboard.add(KeyboardButton(BTN_HELP))
        
        # Отправляем сообщение о начале генерации
        bot.reply_to(message, MSG_TTS_PROCESSING, reply_markup=keyboard)
        
        # Создаем голосовое сообщение
        voice_file = create_voice_message(text, lang_code)
        
        if voice_file:
            # Отправляем голосовое сообщение
            with open(voice_file, 'rb') as audio:
                bot.send_voice(message.chat.id, audio)
            # Удаляем временный файл
            os.unlink(voice_file)
        else:
            bot.reply_to(message, MSG_TTS_ERROR)

    # Команда выбора языка озвучки
    @bot.message_handler(commands=['voice'])
    def cmd_voice(message: Message):
        if not message or not message.from_user:
            return
            
        if not message.text:
            return
            
        command_args = message.text.split()
        if len(command_args) > 1:
            # Если номер языка указан сразу после команды
            process_voice_selection(message, command_args[1])
        else:
            # Создаем клавиатуру с языками и кнопкой отмены
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            # Добавляем кнопки с языками
            for num, (_, lang_name) in TTS_LANGS.items():
                keyboard.add(KeyboardButton(f"{num}. {lang_name}"))
            keyboard.add(KeyboardButton(BTN_CANCEL))
            
            # Показываем текущий язык и меню выбора
            current_lang_num = user_langs.get(message.from_user.id, 1)
            _, current_lang_name = TTS_LANGS.get(current_lang_num, ('ru', '🇷🇺 Русский'))
            msg = bot.reply_to(message, 
                             f"{MSG_VOICE_CURRENT.format(current_lang_name)}\n\n{MSG_VOICE_MENU}", 
                             reply_markup=keyboard)
            # Регистрируем следующий шаг
            bot.register_next_step_handler(msg, process_voice_selection)
            
    def process_voice_selection(message: Message, direct_input: Optional[str] = None):
        if not message or not message.from_user:
            return
            
        # Если пользователь нажал "Отмена" и выбор не был передан напрямую
        if not direct_input and message.text and message.text == BTN_CANCEL:
            # Возвращаем основную клавиатуру
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(BTN_TTS), KeyboardButton(BTN_QUOTES))
            keyboard.add(KeyboardButton(BTN_RANDOM), KeyboardButton(BTN_DAILY))
            keyboard.add(KeyboardButton(BTN_HELP))
            bot.reply_to(message, MSG_CANCELLED, reply_markup=keyboard)
            return
            
        try:
            # Получаем номер языка
            text = direct_input if direct_input else (message.text or "")
            if not text:
                bot.reply_to(message, MSG_VOICE_ERROR)
                return
                
            # Извлекаем первую цифру из текста
            digits = ''.join(filter(str.isdigit, text.split('.')[0]))
            if not digits:
                bot.reply_to(message, MSG_VOICE_ERROR)
                return
                
            lang_number = int(digits)
            if 1 <= lang_number <= len(TTS_LANGS):
                _, lang_name = TTS_LANGS[lang_number]
                if message.from_user and message.from_user.id:
                    user_langs[message.from_user.id] = lang_number
                
                # Возвращаем основную клавиатуру
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(KeyboardButton(BTN_TTS), KeyboardButton(BTN_QUOTES))
                keyboard.add(KeyboardButton(BTN_RANDOM), KeyboardButton(BTN_DAILY))
                keyboard.add(KeyboardButton(BTN_HELP))
                
                bot.reply_to(message, MSG_VOICE_SELECTED.format(lang_name), reply_markup=keyboard)
            else:
                bot.reply_to(message, MSG_VOICE_ERROR)
        except (ValueError, IndexError):
            bot.reply_to(message, MSG_VOICE_ERROR)

    # Команды цитатника
    @bot.message_handler(commands=['quote'])
    def cmd_quote(message: Message):
        if not message or not message.text:
            bot.reply_to(message, MSG_QUOTE_PROMPT)
            return
            
        command_args = message.text.split(maxsplit=1)
        if len(command_args) > 1:
            text = command_args[1]
            # Получаем автора если это ответ на сообщение
            author = None
            user_id = None
            if message.reply_to_message and message.reply_to_message.from_user:
                author = message.reply_to_message.from_user.first_name
                user_id = message.reply_to_message.from_user.id
            
            # Сохраняем цитату
            if quote_manager.add_quote(text, author, message.message_id, message.chat.id):
                bot.reply_to(message, MSG_QUOTE_SAVED)
                
                # Создаем изображение с цитатой
                quote_img = quote_image.create_quote_image(text, author, user_id)
                if quote_img and os.path.exists(quote_img):
                    with open(quote_img, 'rb') as img:
                        bot.send_photo(message.chat.id, img)
                    os.remove(quote_img)
            else:
                bot.reply_to(message, MSG_QUOTE_ERROR)
        else:
            bot.reply_to(message, MSG_QUOTE_PROMPT)

    @bot.message_handler(commands=['random_quote'])
    def cmd_random_quote(message: Message):
        quote = quote_manager.get_random_quote()
        if quote:
            # Получаем информацию из цитаты
            text = quote['text']
            author = quote.get('author')
            user_id = quote.get('user_id')
            user_pic = quote.get('user_pic')
            
            # Создаем изображение со случайной цитатой
            quote_img = quote_image.create_quote_image(
                text, 
                author, 
                user_id=user_id, 
                user_pic_path=user_pic
            )
            
            if quote_img and os.path.exists(quote_img):
                # Добавляем статистику в подпись
                caption = f"{MSG_QUOTE_RANDOM}\n\nВсего цитат: {quote_manager.get_quotes_count()}"
                if author:
                    author_quotes = quote_manager.get_quotes_by_author(author)
                    caption += f"\nЦитат автора {author}: {len(author_quotes)}"
                
                with open(quote_img, 'rb') as img:
                    bot.send_photo(message.chat.id, img, caption=caption)
                os.remove(quote_img)
        else:
            bot.reply_to(message, MSG_QUOTE_EMPTY)

    # Команды рандомайзера
    @bot.message_handler(commands=['random'])
    def cmd_random(message: Message):
        if not message or not message.text:
            bot.reply_to(message, "Формат: /random [мин] [макс]")
            return
            
        try:
            command_args = message.text.split()
            if len(command_args) == 3:  # /random + 2 числа
                min_val = int(command_args[1])
                max_val = int(command_args[2])
                result = random.randint(min_val, max_val)
                bot.reply_to(message, f"🎲 Случайное число: {result}")
            else:
                bot.reply_to(message, "Формат: /random [мин] [макс]")
        except ValueError:
            bot.reply_to(message, "Ошибка! Укажите два целых числа: /random [мин] [макс]")

    @bot.message_handler(commands=['choice'])
    def cmd_choice(message: Message):
        if not message or not message.text:
            bot.reply_to(message, "Формат: /choice вар1, вар2, вар3")
            return
            
        command_args = message.text.split(maxsplit=1)
        if len(command_args) > 1:
            options = command_args[1]
            items = [x.strip() for x in options.split(',')]
            if len(items) > 1:
                choice = random.choice(items)
                bot.reply_to(message, f"🎲 Я выбираю: {choice}")
            else:
                bot.reply_to(message, "Укажите несколько вариантов через запятую")
        else:
            bot.reply_to(message, "Формат: /choice вар1, вар2, вар3")

    @bot.message_handler(commands=['coin'])
    def cmd_coin(message: Message):
        result = random.choice([MSG_COIN_HEADS, MSG_COIN_TAILS])
        bot.reply_to(message, result)

    motivation = [
        "Сегодня отличный день, чтобы сделать шаг к своей мечте! 🚀💪",
        "Не бойся ошибок — они учат тебя быть сильнее. 🔥🛡️",
        "Каждое маленькое действие приближает тебя к большой цели. 🏹✨",
        "Помни: твои усилия сегодня формируют твой успех завтра. 🌱🌞",
        "Не откладывай на завтра то, что можно сделать сегодня. ⏰⚡",
        "Сделай хотя бы один шаг, даже если он маленький — это уже прогресс. 👣💫",
        "Ты сильнее, чем думаешь. Действуй! 💪⚡",
        "Улыбнись — это первый шаг к продуктивному дню. 😄🌟"
    ]
    # Команда совета дня
    @bot.message_handler(commands=['daily'])
    def cmd_daily(message):
        reply = random.choice(motivation)
        bot.reply_to(message, f"📅 Совет дня:\n{reply}")


    # Обработчик текстовых сообщений
    # Реакция на ответ "цитата"
    @bot.message_handler(func=lambda message: message.reply_to_message is not None and 
                        message.text and message.text.lower() in ['цитата', 'quote', 'цытата'])
    def handle_quote_reply(message: Message):
        if not message or not message.reply_to_message:
            return
            
        # Получаем текст из оригинального сообщения
        original_msg = message.reply_to_message
        if not original_msg or not original_msg.text:
            bot.reply_to(message, MSG_QUOTE_NO_TEXT)
            return
            
        # Получаем автора и его id
        author = None
        user_id = None
        user_pic = None
        
        if original_msg.from_user:
            author = original_msg.from_user.first_name
            user_id = original_msg.from_user.id
            
            # Пробуем получить фото пользователя
            try:
                photos = bot.get_user_profile_photos(user_id, limit=1)
                if photos and photos.total_count > 0 and photos.photos:
                    # photos.photos can be a list of lists (sizes) or a flat list depending on library version
                    first_set = photos.photos[0]
                    if isinstance(first_set, list):
                        # choose largest available size (by file_size or width), fallback to last item
                        try:
                            photo = max(first_set, key=lambda p: getattr(p, 'file_size', getattr(p, 'width', 0) or 0))
                        except Exception:
                            photo = first_set[-1] if first_set else None
                    else:
                        photo = first_set
                    if photo and getattr(photo, 'file_id', None):
                        file_info = bot.get_file(photo.file_id)
                        if file_info and file_info.file_path:
                            downloaded_file = bot.download_file(file_info.file_path)
                            
                            # Сохраняем временно
                            temp_pic = f"temp_userpic_{user_id}.jpg"
                            with open(temp_pic, 'wb') as f:
                                f.write(downloaded_file)
                            user_pic = temp_pic
            except Exception as e:
                print(f"Error getting user photo: {e}")
                user_pic = None        # Сохраняем цитату
        if quote_manager.add_quote(
            text=original_msg.text,
            author=author,
            message_id=original_msg.message_id,
            chat_id=message.chat.id,
            user_id=user_id,
            user_pic=user_pic
        ):
            # Создаем изображение с цитатой
            quote_img = quote_image.create_quote_image(
                original_msg.text,
                author,
                user_id=user_id,
                user_pic_path=quote_manager.get_user_pic(user_id) if user_id else None
            )
            
            if quote_img and os.path.exists(quote_img):
                # Добавляем статистику в подпись
                caption = f"{MSG_QUOTE_SAVED}\n\nВсего цитат: {quote_manager.get_quotes_count()}"
                if author:
                    author_quotes = quote_manager.get_quotes_by_author(author)
                    caption += f"\nЦитат автора {author}: {len(author_quotes)}"
                    
                with open(quote_img, 'rb') as img:
                    bot.send_photo(message.chat.id, img, caption=caption)
                os.remove(quote_img)
            
            # Удаляем временный файл аватара
            if user_pic and os.path.exists(user_pic):
                os.remove(user_pic)
        else:
            bot.reply_to(message, MSG_QUOTE_ERROR)
    
    @bot.message_handler(content_types=['text'])
    def handle_text(message: Message):
        if message.text == BTN_TTS:
            # Создаем клавиатуру с кнопкой отмены
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(BTN_CANCEL))
                
            # Просим пользователя ввести текст для озвучки
            msg = bot.reply_to(message, MSG_TTS_PROMPT, reply_markup=keyboard)
            # Регистрируем следующий шаг
            bot.register_next_step_handler(msg, lambda m: process_tts_text(m))
        elif message.text == BTN_QUOTES:
            bot.reply_to(message, MSG_QUOTE_INFO)
        elif message.text == BTN_RANDOM:
            bot.reply_to(message, MSG_RANDOM_INFO)
        elif message.text == BTN_DAILY:
            bot.reply_to(message, MSG_DAILY_INFO)
        elif message.text == BTN_HELP:
            bot.send_message(message.chat.id, MSG_HELP)
