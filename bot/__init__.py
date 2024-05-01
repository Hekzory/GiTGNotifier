import asyncio
import logging

from telegram.ext import ApplicationBuilder

from config import ConfigManager
from database import DatabaseManager
from handlers import register_handlers
from tasks import check_all_for_pr

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    # Loads env variables
    current_config = ConfigManager.get_config()

    # Setup db connection
    logging.getLogger().info("Started db initialization")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(DatabaseManager.setup_db())
    loop.run_until_complete(future)
    logging.getLogger().info("Finished db initialization")

    logging.getLogger().info("Creating application")
    application = ApplicationBuilder().http_version("2").token(current_config['BOT_TOKEN']).build()
    logging.getLogger().info("Adding tasks to job queue")
    job_queue = application.job_queue
    job_notify = job_queue.run_repeating(check_all_for_pr, interval=60 * 60, first=30)
    logging.getLogger().info("Application created")

    register_handlers(application)

    application.run_polling()


if __name__ == '__main__':
    main()
