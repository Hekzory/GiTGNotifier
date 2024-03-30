import os


def load_config():
    return {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
    }
