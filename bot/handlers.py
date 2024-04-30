from typing import Optional

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from models.GHRepository import GHRepository
from utils import check_for_new_pr
from database import add_repository_to_db, get_repositories_from_db, delete_repository_from_db

# TODO: Use DB instead of temp dictionary in memory for storing user preferences
user_repos = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=update.message.text)


async def set_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 2:
        if await add_repository_to_db(GHRepository(update.effective_chat.id, command[1])):
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Tracked repository successfully set to: \n\"" + str(command[1]) + "\"")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Repository "{command[1]}" is already tracking')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/set "
                                            "yourusername/yourreponame\"")


async def delete_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 2:
        rows = await delete_repository_from_db(GHRepository(update.effective_chat.id, command[1]))
        if len(rows) > 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Repository "{command[1]}" removed')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Repository "{command[1]}" not found')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/delete "
                                            "yourusername/yourreponame\"")


async def get_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 1:
        result = await get_repositories_from_db(update.effective_user.id)
        if len(result) > 0:
            text = "Tracked repositories are currently set to: "
            for repository in result:
                text += "\n\"" + repository.full_name + "\""
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Tracked repositories are currently not set.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/get\"")


async def check_for_pr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 1:
        result: Optional[GHRepository] = user_repos.get(update.effective_user.id, None)
        if result is not None:
            answer = await check_for_new_pr(result)
            user_repos.get(update.effective_user.id).update_access_time()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=answer)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Tracked repository is currently not set.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/checkpr\"")


def register_handlers(application):
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    set_handler = CommandHandler("set", set_repository)
    application.add_handler(set_handler)
    get_handler = CommandHandler("get", get_repository)
    application.add_handler(get_handler)
    check_pr_handler = CommandHandler("checkpr", check_for_pr)
    application.add_handler(check_pr_handler)
    delete_handler = CommandHandler("delete", delete_repository)
    application.add_handler(delete_handler)
