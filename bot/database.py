import psycopg

from config import ConfigManager
from models.GHRepository import GHRepository


class DatabaseManager:
    connection = None

    @classmethod
    async def get_db_conn(cls):
        """
        Creates or gets the database connection
        """
        config = ConfigManager.get_config()
        cls.connection = await psycopg.AsyncConnection.connect(
                f"user={config["DB_USER"]} "
                f"password={config["DB_PASS"]} "
                f"dbname={config["DB_NAME"]} "
                f"host={config["DB_HOST"]}"
        )
        return cls.connection

    @classmethod
    async def setup_db(cls):
        """
        Creates initial tables
        """
        async with await cls.get_db_conn() as connection:
            async with connection.transaction():
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS repository (
                        chat_id BIGINT NOT NULL,
                        repo_name TEXT NOT NULL,
                        last_access_time TIMESTAMP NOT NULL
                    );
                ''')

    @classmethod
    async def add_repository_to_db(cls, repository: GHRepository):
        """
        Adds a new repository record to the database
        """
        async with await cls.get_db_conn() as connection:
            async with connection.transaction():
                if await cls.is_new_repository(repository.chat_id, repository.full_name):
                    await connection.execute('''
                        INSERT INTO repository(chat_id, repo_name, last_access_time) VALUES(%s, %s, %s);
                    ''', (repository.chat_id, repository.full_name, repository.last_access_time))
                    return True
                return False

    @classmethod
    async def is_new_repository(cls, chat_id, repository_name):
        """
        Checks if a repository is new
        """
        async with await cls.get_db_conn() as connection:
            async with await connection.execute('''
                SELECT * FROM repository where chat_id = %s and repo_name = %s LIMIT 1;
            ''', (chat_id, repository_name)) as cursor:
                return await cursor.fetchone() is None

    @classmethod
    async def get_repos_by_chat_id(cls, chat_id):
        """
        Gets all repositories by chat id
        """
        async with await cls.get_db_conn() as connection:
            async with connection.transaction():
                async with await connection.execute('''
                    SELECT * FROM repository WHERE chat_id = %s;
                ''', (chat_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [cls.build_repository(row) for row in rows]

    @classmethod
    async def get_unique_chat_ids(cls):
        """
        Gets list of all unique chat ids
        """
        async with await cls.get_db_conn() as connection:
            async with connection.transaction():
                async with await connection.execute('''
                    SELECT DISTINCT chat_id FROM repository;
                ''') as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]

    @classmethod
    async def update_repos_access_time_by_chat_id(cls, chat_id):
        """
        Update last access times based on chat id
        """
        async with await cls.get_db_conn() as connection:
            async with connection.transaction():
                await connection.execute('''
                UPDATE repository SET last_access_time = NOW() WHERE chat_id = %s;
                ''', (chat_id,))

    @classmethod
    async def delete_repository_from_db(cls, repository: GHRepository):
        """
        Deletes a repository from the database by chat id and repository name
        """
        async with await cls.get_db_conn() as connection:
            async with connection.transaction():
                async with await connection.execute('''
                    DELETE FROM repository WHERE chat_id = %s and repo_name = %s RETURNING *
                ''', (repository.chat_id, repository.full_name)) as cursor:
                    return await cursor.fetchall()

    @staticmethod
    def build_repository(row):
        """
        Builds a new repository object from the given row
        """
        return GHRepository(row[0], row[1], row[2])
