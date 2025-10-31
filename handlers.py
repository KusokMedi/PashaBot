from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import random
from lines import *  # Импортируем все сообщения
from typing import Optional

def register_handlers(bot: TeleBot):
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
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                # Генерируем голосовое сообщение
                tts = gTTS(text=text, lang=lang)
                # Сохраняем во временный файл
                tts.save(tmp_file.name)
                return tmp_file.name
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
            return None
    
    # Команда TTS
    @bot.message_handler(commands=['tts'])
    def cmd_tts(message: Message):
        if not message or not message.from_user:
            return
            
        # Создаем клавиатуру с кнопкой отмены
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(BTN_CANCEL))
            
        # Просим пользователя ввести текст для озвучки
        msg = bot.reply_to(message, MSG_TTS_PROMPT, reply_markup=keyboard)
        # Регистрируем следующий шаг
        bot.register_next_step_handler(msg, process_tts_text)
        
    def process_tts_text(message: Message):
        if not message or not message.text or not message.from_user:
            return
            
        # Если пользователь нажал "Отмена"
        if message.text == BTN_CANCEL:
            # Возвращаем основную клавиатуру
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(BTN_TTS), KeyboardButton(BTN_QUOTES))
            keyboard.add(KeyboardButton(BTN_RANDOM), KeyboardButton(BTN_DAILY))
            keyboard.add(KeyboardButton(BTN_HELP))
            bot.reply_to(message, MSG_CANCELLED, reply_markup=keyboard)
            return
            
        text = message.text
        
        # Проверка длины текста
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
        if not message or not message.text or not message.from_user:
            bot.reply_to(message, MSG_VOICE_MENU)
            return
            
        command_args = message.text.split()
        if len(command_args) == 1:
            # Просто команда /voice без аргументов
            current_lang_num = user_langs.get(message.from_user.id, 1)
            _, current_lang_name = TTS_LANGS.get(current_lang_num, ('ru', '🇷🇺 Русский'))
            bot.reply_to(message, MSG_VOICE_CURRENT.format(current_lang_name))
            bot.reply_to(message, MSG_VOICE_MENU)
        else:
            try:
                lang_number = int(command_args[1])
                if 1 <= lang_number <= 6:
                    _, lang_name = TTS_LANGS[lang_number]
                    user_langs[message.from_user.id] = lang_number
                    bot.reply_to(message, MSG_VOICE_SELECTED.format(lang_name))
                else:
                    bot.reply_to(message, MSG_VOICE_ERROR)
            except ValueError:
                bot.reply_to(message, MSG_VOICE_ERROR)

    # Команды цитатника
    @bot.message_handler(commands=['quote'])
    def cmd_quote(message: Message):
        if not message or not message.text:
            bot.reply_to(message, "Укажите текст цитаты после команды /quote")
            return
            
        command_args = message.text.split(maxsplit=1)
        if len(command_args) > 1:
            text = command_args[1]
            bot.reply_to(message, "📝 Цитата сохранена!")
        else:
            bot.reply_to(message, "Укажите текст цитаты после команды /quote")

    @bot.message_handler(commands=['random_quote'])
    def cmd_random_quote(message: Message):
        bot.reply_to(message, "🎲 Случайная цитата из базы...")

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

    # Команда совета дня
    @bot.message_handler(commands=['daily'])
    def cmd_daily(message: Message):
        bot.reply_to(message, "📅 Совет дня...")

    # Обработчик текстовых сообщений
    @bot.message_handler(content_types=['text'])
    def handle_text(message: Message):
        if message.text == BTN_TTS:
            bot.reply_to(message, MSG_TTS_INFO)
        elif message.text == BTN_QUOTES:
            bot.reply_to(message, MSG_QUOTE_INFO)
        elif message.text == BTN_RANDOM:
            bot.reply_to(message, MSG_RANDOM_INFO)
        elif message.text == BTN_DAILY:
            bot.reply_to(message, MSG_DAILY_INFO)
        elif message.text == BTN_HELP:
            bot.send_message(message.chat.id, MSG_HELP)