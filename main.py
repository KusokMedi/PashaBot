import telebot
from telebot.types import Message
from config import TOKEN
from lines import MSG_START, MSG_HELP, MSG_ERROR

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message: Message):
    bot.reply_to(message, MSG_START)

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help_command(message: Message):
    bot.reply_to(message, MSG_HELP)

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    # Здесь будет основная логика обработки сообщений
    bot.reply_to(message, f"Вы написали: {message.text}")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()