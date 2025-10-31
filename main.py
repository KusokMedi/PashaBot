import telebot
import logging
from config import TOKEN
from handlers import register_handlers

# Простое логирование в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Регистрируем все обработчики
register_handlers(bot)

# Запуск бота
if __name__ == "__main__":
    logging.info("Бот запущен...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        bot.stop_polling()
        logging.info("Бот остановлен")