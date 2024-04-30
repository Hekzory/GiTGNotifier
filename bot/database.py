import os
import psycopg

from models.GHRepository import GHRepository


async def create_db_connection():
    """
    Creates the database connection
    """
    return await psycopg.AsyncConnection.connect(
        f"user={os.getenv('POSTGRES_USER')} "
        f"password={os.getenv('POSTGRES_PASSWORD')} "
        f"dbname={os.getenv('POSTGRES_DB')} "
        f"host=bot-db"
    )


async def setup_database():
    """
    Creates tables
    """
    connection = await create_db_connection()
    async with connection.transaction():
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS chat (
            id INT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS repositories (
                chat_id INT NOT NULL REFERENCES chat(id),
                repo_name TEXT NOT NULL,
                last_access_time TIMESTAMP NOT NULL
            )
        ''')
    await connection.close()


async def add_user(chat_id, connection):
    """
    Adds a new user to the database
    """
    await connection.execute('''
            INSERT INTO chat(id) VALUES(%s)
        ''', (chat_id,))


async def add_repository_to_db(repository: GHRepository):
    """
    Adds a new repository to the database and adds new user if it doesn't exist'
    """
    connection = await create_db_connection()
    try:
        async with connection.transaction():
            if await is_new_chat(repository.chat_id, connection):
                await add_user(repository.chat_id, connection)

            if await is_new_repository(repository.chat_id, repository.full_name, connection):
                await connection.execute('''
                    INSERT INTO repositories(chat_id, repo_name, last_access_time) VALUES(%s, %s, %s)
                ''', (repository.chat_id, repository.full_name, repository.last_access_time))
                return True
            else:
                return False
    finally:
        await connection.close()


async def is_new_repository(chat_id, repository_name, connection):
    """
    Checks if a repository is new
    """
    cursor = await connection.execute('''
        SELECT COUNT(*) FROM repositories where chat_id = %s and repo_name = %s
    ''', (chat_id, repository_name))
    result = await cursor.fetchone()
    return result[0] == 0


async def is_new_chat(chat_id, connection):
    """
    Checks if requested user is new
    """
    cursor = await connection.execute('''
        SELECT COUNT(*) FROM chat where id = %s
    ''', (chat_id,))
    result = await cursor.fetchone()
    return result[0] == 0


async def get_repositories_from_db(chat_id):
    """
    Gets all repositories by chat id
    """
    connection = await create_db_connection()
    try:
        async with connection.transaction():
            cursor = await connection.execute('''
                SELECT * FROM repositories WHERE chat_id = %s
            ''', (chat_id,))
            rows = await cursor.fetchall()
            return [build_repository(row) for row in rows]
    finally:
        await connection.close()


async def delete_repository_from_db(repository: GHRepository):
    """
    Deletes a repository from the database by chat id and repository name
    """
    connection = await create_db_connection()
    try:
        async with connection.transaction():
            cursor = await connection.execute('''
                DELETE FROM repositories WHERE chat_id = %s and repo_name = %s RETURNING *
            ''', (repository.chat_id, repository.full_name))
            rows = await cursor.fetchall()
            return rows
    finally:
        await connection.close()


def build_repository(row):
    """
    Builds a new repository object from the given row
    """
    return GHRepository(row[0], row[1], row[2])
