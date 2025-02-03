import os
from pathlib import Path
from dotenv import load_dotenv
import webbrowser

import telebot
from telebot import types

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env', override=True)

bot = telebot.TeleBot(os.getenv('SECRET_KEY'))


@bot.message_handler(commands=['site', 'website'])
def site(message):
    """ Открывает сайт """
    webbrowser.open('https://vc.com')


@bot.message_handler(commands=['start', 'main', 'hello'])
def main(message):
    """ Обработка заданных команд """
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Перейти на сайт')
    markup.row(btn1)
    btn2 = types.KeyboardButton('Удалить фото')
    btn3 = types.KeyboardButton('Изменить текст')
    markup.row(btn2, btn3)

    file = open('./pic.jpg', 'rb')
    bot.send_photo(message.chat.id, file, reply_markup=markup)

    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)

    bot.register_next_step_handler(message, on_click)

def on_click(message):
    """ Будет выполняться первой так как объявлена как register_next_step_handler """
    if message.text == "Перейти на сайт":
        bot.send_message(message.chat.id, 'Website is open')
    elif message.text == "Удалить фото":
        bot.send_message(message.chat.id, 'Photo is deleted')
    elif message.text == "Изменить текст":
        bot.send_message(message.chat.id, 'Text was edited')


# @bot.message_handler(commands=['start', 'main', 'hello'])
# def main(message):
#     """ Обработка заданных команд """
#     bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')


@bot.message_handler(commands=['help'])
def main(message):
    """ Обработка заданных команд """
    bot.send_message(message.chat.id, '<b>Help</b> <em><u>information</u></em>', parse_mode='html')


@bot.message_handler(content_types=['photo', 'audio'])
def get_photo(message):
    """ Обработка полученных фото или аудио """
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти на сайт', url='https://yandex.ru')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Удалить фото', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Изменить текст', callback_data='edit')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Какое красивое фото!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Edit text', callback.message.chat.id, callback.message.message_id)



@bot.message_handler()
def info(message):
    """ Обработка вводимой информации """
    if message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')



bot.polling(non_stop=True)
