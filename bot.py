import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)

from config_reader import config


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(
    token=config.bot_token.get_secret_value(),
    # Параметры по умолчанию
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(F.text, Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Сообщение с <u>HTML-разметкой</u>", parse_mode=ParseMode.HTML)


@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    await message.answer("Сообщение без <u>HTML-разметкой</u>", parse_mode=None)


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply('Это ответ с "ответом"')


# @dp.message(Command("hello"))
# async def cmd_hello(message: types.Message):
#     await message.reply(
#         f"Hello, {html.bold(html.quote(message.form_user.full_name))}",
#         parse_mode=ParseMode.HTML
#     )


@dp.message(Command('hello'))
async def cmd_hello(message: types.message):
    """ Выделяем часть текста в ответе """
    content = Text(
        "Hello, ",
        # Выделяем часть текста
        Bold(message.from_user.full_name)
    )
    await message.answer(
        **content.as_kwargs()
    )


@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: types.Message):
    content = as_list(
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())


# @dp.message(F.text)
# async def echo_with_time(message: types.Message):
#     """ message.text возвращает без форматирования. Еще есть message.md_text """
#     # Получаем текущее время в часовом поясе ПК
#     time_now = datetime.now().strftime('%H:%M')
#     # Создаём подчёркнутый текст
#     added_text = html.underline(f"Создано в {time_now}")
#     # Отправляем новое сообщение с добавленным текстом
#     await message.answer(f"{message.html_text}\n\n{added_text}", parse_mode="HTML")


@dp.message(F.text)
async def extract_data(message: Message):
    """ Достаем из сообщения данные
    '
    привет www.yandex.ru
    завтра parl@mail.ru
    потому что SuperS3cretPa$$w0rd
    '
    """
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            # Неправильно
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # Правильно
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )



@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
