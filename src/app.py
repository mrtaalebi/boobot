import os
import logging
import json


from telegram.ext import Updater, CommandHandler, RegexHandler, ConversationHandler
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup

from src.db import DB, User


class Boobot:

    def __init__(self, bot_token, engine_uri, log_level='INFO'):
        self.updater = Updater(bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.db = DB(engine_uri)

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level={
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
                }[log_level]
        )

 
    def build_callback(self, data):
        return_value = json.dumps(data)
        if len(return_value) > 64:
            raise Exception("Callback data is larger tan 64 bytes")
        return return_value


    def send_keyboard(self, update, keyboard, text):
        reply_keyboard = ReplyKeyboardMarkup([keyboard])
        update.message.reply_text(
            text=text,
            reply_markup=reply_keyboard
        )


    def start(self, update, context):
        user = self.db.get_or_create_user(update.message.from_user)
        keyboard = [
            InlineKeyboardButton(option['text'])
            for option in
                [
                    {
                        'text': 'openconnect',
                        'data': self.build_callback(
                            {
                                'd1': 'oc',
                                'd2': 'm1'
                            })
                    },
                ]    
        ]
        self.send_keyboard(update, keyboard, 'main menu')


    def openconnect(self, update, context):
        keyboard = [
            InlineKeyboardButton('show openconnect data'),
            InlineKeyboardButton('add openconnect account')
        ]
        self.send_keyboard(update, keyboard, 'openconnect')


    def openconnect_show_data(self, update, context):
        oc_config = self.db.get_user(update.message.from_user.id)
        if oc_config == None:
            keyboard = [
                InlineKeyboardButton('add openconnect account'),
                InlineKeyboardButton('main menu'),
            ]
            self.send_keyboard(update, keyboard, 'nothing here!')
        else:
            keyboard = [
                InlineKeyboardButton('main menu'),
            ]
            self.send_keyboard(update, keyboard, str(oc_config))


    def openconnect_add_data(self, update, context):
        user = self.db.get_or_create_user(update.message.from_user.id)
        keyboard = [
            InlineKeyboardButton('openconnect'),
            InlineKeyboardButton('main menu'),
        ]
        msg = 'enter a username for openconnect:'
        self.send_keyboard(update, keyboard, msg)
        return 'openconnect_username'


    def openconnect_add_data_username(self, update, context):
        user = self.db.get_or_create_user(update.message.from_user.id)
        text = update.message.text
        keyboard = [
            InlineKeyboardButton('openconnect'),
            InlineKeyboardButton('main menu'),
        ]
        if re.match(text, '(a-zA-Z)(a-zA-Z0-9)+') and \
                db.query(User, oc_username == text).count() == 0:        
            s = self.db.session()
            user = s.query(User).filter(User.id == user.id).first()
            user.oc_username = text
            s.commit()
            msg = 'now choose a strong password:'
            self.send_keyboard(update, keyboard, msg)
            return 'openconnect_password'
        else:
            msg = (
                    'username must start with a-zA-Z\n'
                    'contain only a-zA-Z0-9\n'
                    'and be atleast 3 characters\n'
            )
            self.send_keyboard(update, keyboard, msg)
            return 'openconnect_username'


    def openconnect_add_data_password(self, update, context):
        user = self.db.get_or_create_user(update.message.from_user.id)
        text = update.message.text
        keyboard = [
            InlineKeyboardButton('openconnect'),
            InlineKeyboardButton('main menu'),
        ]
        if len(text) >= 8:
            s = self.db.session()
            user = s.query(User).filter(User.id == user.id).first()
            user.oc_password = text
            s.commit()
            
            subprocess.run(
                [
                    'ocpasswd',
                    '-c',
                    '/etc/ocserv/pass.wd',
                    user.oc_username
                ],
                input=f'{user.oc_password}\n{user.oc_password}\n',
            )

            msg = 'nice! your openconnect account will be ready in a second.'
            self.send_keyboard(update, keyboard, msg)
            return -1
        else:
            msg = 'password must be >=8 characters'
            self.send_keyboard(update, keyboard, msg)
            return 'openconnect_password'


    def cancel(self, update, context):
        start(update, context)
                    

    def add_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        mainmenu_handler = RegexHandler('^main menu$', self.start)
        self.dispatcher.add_handler(mainmenu_handler)

        openconnect_handler = RegexHandler('^openconnect$', self.openconnect)
        self.dispatcher.add_handler(openconnect_handler)

        openconnect_show_data_handler = \
            RegexHandler('^show openconnect data$', self.openconnect_show_data)
        self.dispatcher.add_handler(openconnect_show_data_handler)

        openconnect_add_data_handler = ConversationHandler(
            entry_points=[RegexHandler(
                '^add openconnect account$',
                self.openconnect_add_data)],
            states={
                'openconnect_username': [RegexHandler('^.*|/cancel$', self.openconnect_add_data_username)],
                'openconnect_password': [RegexHandler('^.*|/cancel$', self.openconnect_add_data_password)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )


    def run(self):
        self.add_handlers()
        self.updater.start_polling()
