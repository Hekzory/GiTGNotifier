from telegram.ext import ContextTypes

from database import DatabaseManager
from utils import check_for_pr_auto, check_for_commits_auto


async def check_all_for_pr(context: ContextTypes.DEFAULT_TYPE):
    """
    Utility function for checking all users' repos for new PRs since last access time
    Called automatically by PTG job scheduler
    """
    chat_ids = await DatabaseManager.get_unique_chat_ids()
    messages = dict()
    for chat_id in chat_ids:
        messages[chat_id] = await check_for_pr_auto(chat_id)
        if len(messages[chat_id]) > 0:
            messages[chat_id] = "Automatic check: \n" + messages[chat_id]
            await context.bot.send_message(chat_id=chat_id, text=messages[chat_id])


async def check_all_for_commits(context: ContextTypes.DEFAULT_TYPE):
    """
    Utility function for checking all users' repos for new commits since last access time
    Called automatically by PTG job scheduler
    """
    chat_ids = await DatabaseManager.get_unique_chat_ids()
    messages = dict()
    for chat_id in chat_ids:
        messages[chat_id] = await check_for_commits_auto(chat_id)
        if len(messages[chat_id]) > 0:
            messages[chat_id] = "Automatic check: \n" + messages[chat_id]
            await context.bot.send_message(chat_id=chat_id, text=messages[chat_id])
