import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from database import DatabaseManager
from models.GHRepository import GHRepository
from utils import check_for_pr


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I am a bot which is responsible for tracking GitHub PRs.")


async def set_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 2:
        if await DatabaseManager.add_repository_to_db(GHRepository(update.effective_chat.id, command[1])):
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Tracked repository successfully added: \n\"" + str(command[1]) + "\"")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Repository "{command[1]}" is already being tracked')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/set "
                                            "yourusername/yourreponame\"")


async def delete_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 2:
        rows = await DatabaseManager.delete_repository_from_db(GHRepository(update.effective_chat.id, command[1]))
        if len(rows) > 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Repository "{command[1]}" removed')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Repository "{command[1]}" already not present')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/delete "
                                            "yourusername/yourreponame\"")


async def get_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 1:
        result = await DatabaseManager.get_repos_by_chat_id(update.effective_chat.id)
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


async def check_for_pr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) == 1:
        text = await check_for_pr(update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/checkpr\"")


def register_handlers(application):
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    set_handler = CommandHandler("set", set_repository)
    application.add_handler(set_handler)
    get_handler = CommandHandler("get", get_repository)
    application.add_handler(get_handler)
    check_pr_handler = CommandHandler("checkpr", check_for_pr_handler)
    application.add_handler(check_pr_handler)
    delete_handler = CommandHandler("delete", delete_repository)
    application.add_handler(delete_handler)
    logging.getLogger().info("Handlers registered")
