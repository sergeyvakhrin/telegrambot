import os
import json
from pathlib import Path

import requests
import telebot
from dotenv import load_dotenv
from currency_converter import CurrencyConverter
from telebot import types

currency = CurrencyConverter()

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env', override=True)

bot = telebot.TeleBot(os.getenv('SECRET_KEY'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет! Введите сумму:')
    bot.register_next_step_handler(message, summa)


def summa(message):
    try:
        amount = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Нужно вводить цифры.")
        bot.register_next_step_handler(message, summa)
        return
    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data=f'usd/eur;{amount}')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data=f'eur/usd;{amount}')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data=f'usd/gbp;{amount}')
        btn4 = types.InlineKeyboardButton('Другое значение', callback_data=f'else;{amount}')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите пару валют:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Число должно быть больше нуля.")
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    values = call.data.split(';')[0].upper().split('/')
    amount = call.data.split(';')[1]
    if values[0] != 'ELSE':
        res = currency.convert(amount, values[0], values[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f'Результат конвертации валют: {call.data.upper()} {amount} = {round(res, 2)}.\n\n')
        bot.send_message(call.message.chat.id, 'Следующий запрос:')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Введите пару значение через слэш:')
        bot.register_next_step_handler(call.message, my_currency, amount)


def my_currency(message, amount):
    try:
        values = message.text.split(';')[0].upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Результат конвертации валют: {message.text.upper()} {amount} = {round(res, 2)}.\n\n')
        bot.send_message(message.chat.id, 'Следующий запрос:')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, f'Не верный ввод. Попробуйте еще раз (пример: usd/eur):')
        bot.register_next_step_handler(message, my_currency, amount)


    # TODO: глюк, если несколько раз нажать на кнопки при одном запросе. Сколько нажмешь, столько и вызовет функцию summa
    # Решение - удалять кнопки или дисэйблить

    # Избавляемся от глобальной переменной
    # В передаче
    # ..., callback_data=f'usd/eur;{amount}')
    #
    # В функции
    # values = call.data.split(';')[0].upper().split('/')
    # amount = call.data.split(';')[1]

bot.polling(non_stop=True)
