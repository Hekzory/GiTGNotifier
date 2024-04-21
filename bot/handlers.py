from typing import Optional

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from models.GHRepository import GHRepository
from utils import check_for_new_pr

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
    if len(command) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/set "
                                            "yourusername/yourreponame\"")
    user_repos[update.effective_user.id] = GHRepository(command[1])
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Tracked repository successfully set to: \n\"" + str(command[1]) + "\"")


async def get_repository(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/get\"")
    result: Optional[GHRepository] = user_repos.get(update.effective_user.id, None)
    if result is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Tracked repository is currently set to: \n\"" +
                                            result.full_name + "\"")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Tracked repository is currently not set.")


async def check_for_pr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip().split()
    if len(command) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Incorrect argument count. Correct example: \n\"/checkpr\"")
    result: Optional[GHRepository] = user_repos.get(update.effective_user.id, None)
    if result is not None:
        answer = await check_for_new_pr(result)
        user_repos.get(update.effective_user.id).update_access_time()
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=answer)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Tracked repository is currently not set.")


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
