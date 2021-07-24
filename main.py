import logging
import datetime
import json
import pytz

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from utils import workflow

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open("secret.json", "r") as secret:
    data = json.load(secret)
    token = data["token"]
    channel_id = data["channel_id"]


def start_command(update: Update, context: CallbackContext):
    bot = Bot(token=token)
    update.message.reply_text("Hey there!")


def morning(context: CallbackContext):
    message = workflow()
    if not message:
        message = "No important news for today"
    context.bot.send_message(channel_id, text=message, parse_mode="HTML", disable_web_page_preview=True)


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('This bot is used in CTI News channel')


def main():
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    j = updater.job_queue
    j.run_daily(morning, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=9, minute=30, second=00, tzinfo=pytz.timezone('Europe/Kiev')))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
