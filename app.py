import os
import logging


from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Boobot:

    def __init__(self, bot_token, log_level='INFO'):
        self.updater = Updater(bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level={
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
                }[log_level]
        )


    def start(self, update, context):
        keyboard = [
            InlineKeyboardButton('get telegram proxy'),
            InlineKeyboardButton('get openconnect data'),
            InlineKeyboardButton('get openvpn data'),
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.message.reply_text(
            'hello',
            reply_markup=reply_markup,
        )


    def add_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)


    def run(self):
        self.add_handlers()
        self.updater.start_polling()
