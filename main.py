from pathlib import Path

import requests
import telebot
import json
import os

from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import whitelist

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env', override=True)

token_api_sandbox = os.getenv('Authorization')
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))


def white_user(user_id):
    """ Валидация на белый список """
    if user_id in whitelist:
        return True


def validated_imei(message) -> bool:
    """ Проверяет введенные данные """
    if white_user(message.from_user.id):
        imei = message.text
        if len(imei) != 15:
            bot.send_message(message.chat.id, f"Вы ввели не верный IMEI! Должен состоять из 15-ти цифр.")
            return False
        for i in imei:
            if not i.isdigit():
                bot.send_message(message.chat.id, f"Вы ввели не верный IMEI! Должен состоять из 15-ти цифр.")
                return False
        return True
    else:
        bot.send_message(message.chat.id, 'Вы не имеете доступа к запросу!')


def response_imei(message):
    """ Делаем API запрос """
    imei = message.text
    url = "https://api.imeicheck.net/v1/checks"
    payload = json.dumps({
        "deviceId": imei,
        "serviceId": 12
    })
    headers = {
        'Authorization': token_api_sandbox,
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    if response.get('properties'):
        response = response['properties']
        bot.send_message(message.chat.id, f'Модель {response['deviceName']}\n'
                                          f'IMEI2 {response['imei2']}\n'
                                          f'Серийный номер {response['serial']}')
    else:
        bot.reply_to(message, "Введен не существующий IMEI")


def process_imei(message) -> None:
    """ Выводит данные в Телеграм """
    imei = message.text
    if validated_imei(message):
        bot.send_message(message.chat.id, f"Вы ввели: {imei}")
        response_imei(message)



@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Начать", callback_data="start"))
    bot.send_message(message.chat.id, "Привет!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "start":
        bot.send_message(call.message.chat.id, "Введите IMEI:")
        bot.register_next_step_handler(call.message, process_imei)


@bot.message_handler()
def spase_input(message):
    """ Игнорируем start """
    imei = message.text
    if validated_imei(message):
        bot.send_message(message.chat.id, f"Вы ввели: {imei}")
        response_imei(message)


bot.polling(none_stop=True)
