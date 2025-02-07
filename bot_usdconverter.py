import os
import json
from pathlib import Path

import requests
import telebot
from dotenv import load_dotenv
from currency_converter import CurrencyConverter
from telebot import types

currency = CurrencyConverter()
amount = 0

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env', override=True)

bot = telebot.TeleBot(os.getenv('SECRET_KEY'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет! Введите сумму:')
    bot.register_next_step_handler(message, summa)


def summa(message):
    global amount
    try:
        amount = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Нужно вводить цифры. Вместо запятой, поставьте точку.")
        bot.register_next_step_handler(message, summa)
        return
    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Другое значение', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите пару валют:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Число должно быть больше нуля.")
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Результат конвертации валют: {round(res, 2)}.\n\n')
        bot.send_message(call.message.chat.id, 'Следующий запрос:')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введите пару значение через слэш:')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Результат конвертации валют: {round(res, 2)}.\n\n')
        bot.send_message(message.chat.id, 'Следующий запрос:')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, f'Не верный ввод. Попробуйте еще раз (пример: usd/eur):')
        bot.register_next_step_handler(message, my_currency)


    # TODO: глюк, если несколько раз нажать на кнопки при одном запросе. Сколько нажмешь, столько и вызовет функцию summa


bot.polling(non_stop=True)
