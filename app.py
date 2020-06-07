import os
import logging

from telegram.ext import Updater, CommandHandler


updater = Updater(token=os.environ.get('BOT_TOKEN'), use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start(update, context):
    keyboard = [
        InlineKeyboardButton('get telegram proxy'),
        InlineKeyboardButton('get openconnect data'),
        InlineKeyboardButton('get openvpn data'),
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.message.chat_id,
        reply_markup=reply_markup,
    )


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
