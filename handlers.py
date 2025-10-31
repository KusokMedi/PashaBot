from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import random

def register_handlers(bot: TeleBot):
    # Команда /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("🎤 TTS"), KeyboardButton("📝 Цитаты"))
        keyboard.add(KeyboardButton("🎲 Рандом"), KeyboardButton("📅 Совет дня"))
        keyboard.add(KeyboardButton("❓ Помощь"))
        
        bot.reply_to(message, 
                    "Привет! Я Паша Бот 🤖\nВыбери функцию в меню ниже:",
                    reply_markup=keyboard)

    # Команда /help
    @bot.message_handler(commands=['help'])
    def cmd_help(message: Message):
        help_text = """
        🤖 Доступные команды:
        
        Основные:
        /start - Перезапустить бота
        /help - Показать это сообщение
        
        Text-to-Speech:
        /tts - Озвучить текст
        /voice - Сменить голос
        
        Цитатник:
        /quote - Сохранить цитату
        /random_quote - Случайная цитата
        
        Рандомайзер:
        /random - Случайное число
        /choice - Выбрать вариант
        /coin - Подбросить монетку
        
        Разное:
        /daily - Совет дня
        """
        bot.reply_to(message, help_text)

    # Команды TTS
    @bot.message_handler(commands=['tts'])
    def cmd_tts(message: Message):
        if not message or not message.text:
            bot.reply_to(message, "Укажите текст после команды /tts")
            return
            
        command_args = message.text.split(maxsplit=1)
        if len(command_args) > 1:
            text = command_args[1]
            bot.reply_to(message, "🎤 Генерирую голосовое сообщение...")
        else:
            bot.reply_to(message, "Укажите текст после команды /tts")

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
        result = random.choice(['Орёл', 'Решка'])
        bot.reply_to(message, f"🎲 {result}!")

    # Команда совета дня
    @bot.message_handler(commands=['daily'])
    def cmd_daily(message: Message):
        bot.reply_to(message, "📅 Совет дня...")

    # Обработчик текстовых сообщений
    @bot.message_handler(content_types=['text'])
    def handle_text(message: Message):
        if message.text == "🎤 TTS":
            bot.reply_to(message, "Отправьте текст для озвучки или используйте /tts [текст]")
        elif message.text == "📝 Цитаты":
            bot.reply_to(message, "Используйте:\n/quote - сохранить\n/random_quote - случайная цитата")
        elif message.text == "🎲 Рандом":
            bot.reply_to(message, "Доступные команды:\n/random - число\n/choice - выбор\n/coin - монетка")
        elif message.text == "📅 Совет дня":
            bot.reply_to(message, "Используйте /daily для получения совета дня")
        elif message.text == "❓ Помощь":
            bot.send_message(message.chat.id, "/help - список всех команд")