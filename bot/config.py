import os


class ConfigManager:
    _config = None

    @classmethod
    def get_config(cls):
        if cls._config is None:
            cls._config = {
                'BOT_TOKEN': os.getenv('BOT_TOKEN'),
                'DB_USER':   os.getenv('POSTGRES_USER'),
                'DB_PASS':   os.getenv('POSTGRES_PASSWORD'),
                'DB_NAME':   os.getenv('POSTGRES_DB'),
                'DB_HOST':   "bot-db",
            }
        return cls._config
