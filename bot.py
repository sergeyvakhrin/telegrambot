import asyncio
import logging
import os
from contextlib import suppress
from datetime import datetime
from random import randint
from typing import Optional

from aiogram import Bot, Dispatcher, types, F, html, flags
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswerMiddleware, CallbackAnswer
from aiogram.utils.formatting import Text
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.markdown import hide_link
from aiogram.utils.media_group import MediaGroupBuilder

from config_reader import config
from handlers import questions, different_types

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
# @dp.message(F.text, Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Сообщение с <u>HTML-разметкой</u>", parse_mode=ParseMode.HTML)


# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     kb = [
#         [types.KeyboardButton(text="С пюрешкой")],
#         [types.KeyboardButton(text="Без пюрешки")]
#     ]
#     keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
#     await message.answer("Как подавать котлеты?", reply_markup=keyboard)


# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     """ Делаем обычные кнопки """
#     kb = [
#         [
#             types.KeyboardButton(text="С пюрешкой"),
#             types.KeyboardButton(text="Без пюрешки")
#         ],
#     ]
#     keyboard = types.ReplyKeyboardMarkup(
#         keyboard=kb,
#         resize_keyboard=True,
#         input_field_placeholder="Выберите способ подачи"
#     )
#     # await message.answer("Как подавать котлеты?", reply_markup=keyboard)
#     await message.answer("Как подавать котлеты?", reply_markup=keyboard)


@dp.message(F.text.lower() == "с пюрешкой")
async def with_puree(message: types.Message):
    """ Обрабатываем нажатие кнопки и удаляем кнопки. Можно вывести другие кнопки """
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.lower() == "без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!", reply_markup=types.ReplyKeyboardRemove())


@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


# У объекта обычной клавиатуры есть ещё две полезных опции:
# one_time_keyboard для автоматического скрытия кнопок после нажатия и
# selective для показа клавиатуры лишь некоторым участникам группы.
# Их использование остаётся для самостоятельного изучения.
# https://core.telegram.org/bots/api#replykeyboardmarkup


@dp.message(Command("special_buttons"))
async def cmd_special_buttons(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # метод row позволяет явным образом сформировать ряд
    # из одной или нескольких кнопок. Например, первый ряд
    # будет состоять из двух кнопок...
    builder.row(
        types.KeyboardButton(text="Запросить геолокацию", request_location=True),
        types.KeyboardButton(text="Запросить контакт", request_contact=True)
    )
    # ... второй из одной ...
    builder.row(types.KeyboardButton(
        text="Создать викторину",
        request_poll=types.KeyboardButtonPollType(type="quiz"))
    )
    # ... а третий снова из двух
    builder.row(
        types.KeyboardButton(
            text="Выбрать премиум пользователя",
            request_user=types.KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        types.KeyboardButton(
            text="Выбрать супергруппу с форумами",
            request_chat=types.KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
                chat_is_forum=True
            )
        )
    )
    # WebApp-ов пока нет, сорри :(

    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

# две заготовки хэндлеров на приём нажатий от нижних двух кнопок

@dp.message(F.user_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.user_shared.request_id}. "
        f"User ID: {message.user_shared.user_id}"
    )


@dp.message(F.chat_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.chat_shared.request_id}. "
        f"User ID: {message.chat_shared.chat_id}"
    )


########## InlineKeyboardBuilder


@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    builder.row(types.InlineKeyboardButton(
        text="Оф. канал Telegram",
        url="tg://resolve?domain=telegram")
    )

    # Чтобы иметь возможность показать ID-кнопку,
    # У юзера должен быть False флаг has_private_forwards
    # user_id = 1234567890
    # chat_info = await bot.get_chat(user_id)
    # if not chat_info.has_private_forwards:
    #     builder.row(types.InlineKeyboardButton(
    #         text="Какой-то пользователь",
    #         url=f"tg://user?id={user_id}")
    #     )

    await message.answer(
        'Выберите ссылку',
        reply_markup=builder.as_markup(),
    )


@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    """ Обрабатываем нажатие кнопки """
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )
    # или просто await callback.answer()

# В функции send_random_value мы вызывали метод answer() не у message,
# а у callback.message. Это связано с тем, что колбэк-хэндлеры работают
# не с сообщениями (тип Message), а с колбэками (тип CallbackQuery),
# у которого другие поля, и само сообщение — всего лишь его часть. Учтите также,
# что message — это сообщение, к которому была прицеплена кнопка (т.е. отправитель
# такого сообщения — сам бот). Если хотите узнать, кто нажал на кнопку,
# смотрите поле from (в вашем коде это будет callback.from_user,
# т.к. слово from зарезервировано в Python)


# Здесь хранятся пользовательские данные.
# Т.к. это словарь в памяти, то при перезапуске он очистится
user_data = {}

def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr")
        ],
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_num_text(message: types.Message, new_value: int):
    await message.edit_text(
        f"Укажите число: {new_value}",
        reply_markup=get_keyboard()
    )


# async def update_num_text(message: types.Message, new_value: int):
#     """ Что бы исключить ошибку """
#     with suppress(TelegramBadRequest):
#         await message.edit_text(
#             f"Укажите число: {new_value}",
#             reply_markup=get_keyboard()
#         )


@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value+1
        await update_num_text(callback.message, user_value+1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value-1
        await update_num_text(callback.message, user_value-1)
    elif action == "finish":
        await callback.message.edit_text(f"Итого: {user_value}")

    await callback.answer()


############ Фабрика колбэков


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int] = None


def get_keyboard_fab():
    """ Генерация клавиатуры """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2)
    )
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="+2", callback_data=NumbersCallbackFactory(action="change", value=2)
    )
    builder.button(
        text="Подтвердить", callback_data=NumbersCallbackFactory(action="finish")
    )
    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()


async def update_num_text_fab(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите число: {new_value}",
            reply_markup=get_keyboard_fab()
        )

@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())


# Нажатие на одну из кнопок: -2, -1, +1, +2
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()


# Нажатие на кнопку "подтвердить"
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"Итого: {user_value}")
    await callback.answer()


###############################################

#### Авто колбэки

# dp = Dispatcher()
# dp.callback_query.middleware(CallbackAnswerMiddleware())


# dp.callback_query.middleware(
#     CallbackAnswerMiddleware(
#         pre=True, text="Готово!", show_alert=True
#     )
# )


# @dp.callback_query()
# async def my_handler(callback: CallbackQuery, callback_answer: CallbackAnswer):
#     ... # тут какой-то код
#     if <everything is ok>:
#         callback_answer.text = "Отлично!"
#     else:
#         callback_answer.text = "Что-то пошло не так. Попробуйте позже"
#         callback_answer.cache_time = 10
#     ... # тут какой-то код


# @dp.callback_query()
# @flags.callback_answer(pre=False)  # переопределяем флаг pre
# async def my_handler(callback: CallbackQuery, callback_answer: CallbackAnswer):
#     ... # тут какой-то код
#     if <everything is ok>:
#         callback_answer.text = "Теперь этот текст будет видно!"
#     ... # тут какой-то код


##################################









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



    dp.include_routers(questions.router, different_types.router)
    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
