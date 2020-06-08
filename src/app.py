import os
import logging
import json
import re
import subprocess

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup

from src.db import DB, User


class Boobot:

    def __init__(self, bot_token, admin_id, engine_uri, oc_host, log_level='INFO'):
        self.updater = Updater(bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.input_dispatcher = \
            {
                #user_id: callback_function
        }

        self.db = DB(engine_uri)
        
        self.oc_host = oc_host

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

    
    def check_user(func):
        def wrapper(self, *args, **kwargs):
            update, context = args[1], args[2]
            user = update.message.from_user
            if self.db.get_user(user).count() == 0:
                admin_msg = (
                    'HEY ADMIN!\n'
                    f'following user wants to join {user.id} {user.username}\n'
                    'add them with ADD_USER <user_id> command\n'
                )
                context.bot.send_message(self.admin_id, admin_msg)
                msg = (
                    'admin has been informed about your request.\n'
                    'they may contact you soon!\n'
                )
                update.message.reply_text(text=msg)
                return
            return func(*args, **kwargs)
        return wrapper


    def admin_add_user(self, update, context):
        user_id = update.message.from_user['id']
        if user_id != self.admin_id:
            msg = \
                'BITCH YOU THOUGHT YOU CAN SEND ADMIN COMMANDS?'
            update.message.reply_text(text=msg)
            return
        
        text = update.message.text
        user_id = text[1]
        chat = context.bot.get_chat(user_id)
        self.db.create_user(chat)
        msg = 'Horray! now you\'re registered!'
        context.bot.send_message(user_id, msg)


    @check_user
    def start(self, update, context):
        user = self.db.get_user(update.message.from_user)
        keyboard = [
            InlineKeyboardButton(option['text'])
            for option in
                [
                    {
                        'text': 'openconnect',
                    },
                ]    
        ]
        self.send_keyboard(update, keyboard, 'main menu')

    
    @check_user
    def openconnect(self, update, context):
        keyboard = [
            InlineKeyboardButton('show openconnect data'),
            InlineKeyboardButton('add openconnect data')
        ]
        self.send_keyboard(update, keyboard, 'openconnect')


    @check_user
    def openconnect_show_data(self, update, context):
        user = self.db.get_user(update.message.from_user)

        if user == None:
            keyboard = [
                InlineKeyboardButton('add openconnect data'),
                InlineKeyboardButton('main menu'),
            ]
            self.send_keyboard(update, keyboard, 'nothing here!')
        else:
            keyboard = [
                InlineKeyboardButton('main menu'),
            ]
            self.send_keyboard(update, keyboard,
                (
                    f'host: {self.oc_host}\n'
                    f'user: {user.oc_username}\n'
                    f'pass: {user.oc_password}\n'
                )
            )


    @check_user
    def openconnect_add_data(self, update, context):
        user = self.db.get_user(update.message.from_user)
        keyboard = [
            InlineKeyboardButton('main menu'),
        ]
        if user.oc_username and user.oc_passowrd:
            msg = 'you already have an openconnect account'
            keyboard.append(InlineKeyboardButton('show openconnect data'))
        else:
            msg = 'enter a username for openconnect:'
            self.input_dispatcher[user.id] = self.openconnect_add_data_username
        self.send_keyboard(update, keyboard, msg)


    @check_user
    def openconnect_add_data_username(self, update, context):
        user = self.db.get_user(update.message.from_user)
        text = update.message.text
        keyboard = [
            InlineKeyboardButton('openconnect'),
            InlineKeyboardButton('main menu'),
        ]
        if re.match('\w{3,}', text):
            users = self.db.query(User, User.oc_username == text)
            if users.count() == 1 and users.first().id != user.id:
                msg = 'a user has already choosen this username!'
            else:
                s = self.db.session()
                user = s.query(User).filter(User.id == user.id).first()
                user.oc_username = text
                s.commit()
                msg = 'now choose a strong password:'
                self.input_dispatcher[user.id] = self.openconnect_add_data_password
        else:
            msg = (
                    'username must start with a-zA-Z\n'
                    'contain only a-zA-Z0-9\n'
                    'and be atleast 3 characters\n'
            )
        self.send_keyboard(update, keyboard, msg)


    @check_user
    def openconnect_add_data_password(self, update, context):
        user = self.db.get_user(update.message.from_user)
        text = update.message.text
        keyboard = [
            InlineKeyboardButton('openconnect'),
            InlineKeyboardButton('main menu'),
        ]
        if 8 <= len(text) <= 128:
            s = self.db.session()
            user = s.query(User).filter(User.id == user.id).first()
            user.oc_password = text
            s.commit()
            
            subprocess.run(
                [
                    'ocpasswd',
                    '-c',
                    '/etc/ocserv/pass.wd',
                    user.oc_username,
                    '<<<',
                    f'{user.oc_password}\n{user.oc_password}\n',
                ]
            )

            msg = 'nice! your openconnect account will be ready in a second.'
            self.send_keyboard(update, keyboard, msg)
            self.input_dispatcher[user.id] = None
        else:
            msg = 'password must be between 8 and 128 characters'
            self.send_keyboard(update, keyboard, msg)


    @check_user
    def user_input(self, update, context):
        user_id = update.message.from_user.id
        if user_id in self.input_dispatcher:
            return self.input_dispatcher[user_id](update, context)
        else:
            keyboard = [
                InlineKeyboardButton('main menu'),
            ]
            msg = 'can\'t understand what to do'
            self.send_keyboard(update, keyboard, msg)


    def add_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        admin_add_user_handler = MessageHandler(Filters.regex('^ADD_USER \w+$'), self.admin_add_user)
        self.dispatcher.add_handler(admin_add_user_handler)

        mainmenu_handler = MessageHandler(Filters.regex('^main menu$'), self.start)
        self.dispatcher.add_handler(mainmenu_handler)

        openconnect_handler = MessageHandler(Filters.regex('^openconnect$'), self.openconnect)
        self.dispatcher.add_handler(openconnect_handler)

        openconnect_show_data_handler = \
            MessageHandler(Filters.regex('^show openconnect data$'), self.openconnect_show_data)
        self.dispatcher.add_handler(openconnect_show_data_handler)

        openconnect_add_data_handler = \
            MessageHandler(Filters.regex('^add openconnect data$'), self.openconnect_add_data)
        self.dispatcher.add_handler(openconnect_add_data_handler)

        user_input_handler = MessageHandler(Filters.regex('.*'), self.user_input)
        self.dispatcher.add_handler(user_input_handler)


    def run(self):
        self.add_handlers()
        self.updater.start_polling()
