import logging

from telegram.ext import ApplicationBuilder

from config import load_config
from handlers import register_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    current_config = load_config()
    application = ApplicationBuilder().http_version("2").token(
        current_config['BOT_TOKEN']).build()
    register_handlers(application)
    application.run_polling()


if __name__ == '__main__':
    main()
