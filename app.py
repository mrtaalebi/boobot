import os
import logging

from telegram.ext import Updater, CommandHandler


updater = Updater(token=os.environ.get('BOT_TOKEN'))
dispatcher = updater.dispatcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
        text="I'm juggernaut, bitch!"
    )

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
