import os
import json
from pathlib import Path

import requests
import telebot
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env', override=True)

bot = telebot.TeleBot(os.getenv('SECRET_KEY'))

API_KEY = os.getenv('API_OPENWEATHERMAP')
# url_openweathermap='https://api.openweathermap.org/data/2.5/'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет {message.from_user.last_name}. Напиши название города:')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    # a = 'Seattle'
    city = message.text.strip().lower()

    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric')
    # data = response.json() # тоже самое, что и следующая строчка
    if response.status_code == 200:
        data = json.loads(response.text)
        temp = data['main']['temp']
        bot.reply_to(message, f'Погода в {city.capitalize()} сейчас {temp}')

        image = 'sunny.png' if temp > 5 else 'couldy.png'
        file = open('./pic/' + image, 'rb')
        bot.send_photo(message.chat.id, file)
    else:
        bot.reply_to(message, f'Город {city.capitalize()} не существует. Проверьте введенное название.')



bot.polling(non_stop=True)
