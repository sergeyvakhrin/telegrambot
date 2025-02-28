import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.markdown import hide_link
from aiogram.utils.media_group import MediaGroupBuilder

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


# @dp.message(F.text)
# async def extract_data(message: Message):
    """ Достаем из сообщения данные
    '
    привет www.yandex.ru
    завтра parl@mail.ru
    потому что SuperS3cretPa$$w0rd
    '
    """
#     data = {
#         "url": "<N/A>",
#         "email": "<N/A>",
#         "code": "<N/A>"
#     }
#     entities = message.entities or []
#     for item in entities:
#         if item.type in data.keys():
#             # Неправильно
#             # data[item.type] = message.text[item.offset : item.offset+item.length]
#             # Правильно
#             data[item.type] = item.extract_from(message.text)
#     await message.reply(
#         "Вот что я нашёл:\n"
#         f"URL: {html.quote(data['url'])}\n"
#         f"E-mail: {html.quote(data['email'])}\n"
#         f"Пароль: {html.quote(data['code'])}"
#     )


@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    """ Создаем команды с аргументами """
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )


# @dp.message(Command("custom1", prefix="%"))
# async def cmd_custom1(message: Message):
    """ Меняем префикс """
#     await message.answer("Вижу команду!")
#
#
# # Можно указать несколько префиксов....vv...
# @dp.message(Command("custom2", prefix="/!"))
# async def cmd_custom2(message: Message):
#     """ Делаем несколько префиксов """
#     await message.answer("И эту тоже вижу!")


@dp.message(F.animation)
async def echo_gif(message: Message):
    """ Отправка ответом тойже гифки, что отправил пользователь """
    await message.reply_animation(message.animation.file_id)


@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []

    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим"
    # открытием файла через `open()`. Но, вообще говоря, этот способ
    # лучше всего подходит для отправки байтов из оперативной памяти
    # после проведения каких-либо манипуляций, например, редактированием через Pillow
    # with open("pic/couldy.png", "rb") as image_from_buffer:
    #     result = await message.answer_photo(
    #         BufferedInputFile(
    #             image_from_buffer.read(),
    #             filename="image from buffer.jpg"
    #         ),
    #         caption="Изображение из буфера",
    #         # Текст сверху
    #         show_caption_above_media=True
    #     )
    #     file_ids.append(result.photo[-1].file_id)

    # Отправка файла из файловой системы
    image_from_pc = FSInputFile("pic/couldy.png")
    result = await message.answer_photo(
        image_from_pc,
        caption="Изображение из файла на компьютере",
        show_caption_above_media=True
    )
    file_ids.append(result.photo[-1].file_id)
    #
    # # Отправка файла по ссылке
    # image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    # result = await message.answer_photo(
    #     image_from_url,
    #     caption="Изображение по ссылке"
    # )
    # file_ids.append(result.photo[-1].file_id)
    # await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))


@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    """ Скачивание файла на сервер """
    await bot.download(
        message.photo[-1],
        destination=f"./tmp/{message.photo[-1].file_id}.jpg"
    )

@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        # для Windows пути надо подправить
        destination=f"./tmp/{message.sticker.file_id}.webp"
    )


# @dp.message(Command("album"))
# async def cmd_album(message: Message):
#     album_builder = MediaGroupBuilder(
#         caption="Общая подпись для будущего альбома"
#     )
#     album_builder.add(
#         type="photo",
#         media=FSInputFile("image_from_pc.jpg")
#         # caption="Подпись к конкретному медиа"
#
#     )
#     # Если мы сразу знаем тип, то вместо общего add
#     # можно сразу вызывать add_<тип>
#     album_builder.add_photo(
#         # Для ссылок или file_id достаточно сразу указать значение
#         media="https://picsum.photos/seed/groosha/400/300"
#     )
#     album_builder.add_photo(
#         media="<ваш file_id>"
#     )
#     await message.answer_media_group(
#         # Не забудьте вызвать build()
#         media=album_builder.build()
#     )


@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    """ Сервисные сообщения """
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию
        # (на скриншоте выше у юзеров нет фамилии)
        await message.reply(f"Привет, {user.full_name}")


@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    """ Скрываем ссылку """
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
