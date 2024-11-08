import asyncio
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from dotenv import load_dotenv

from keyboards.inline_kb import *
from keyboards.reply_kb import *
from database.db_utils import *
from utils.caption import *

load_dotenv()
TOKEN = getenv('TOKEN')
dp = Dispatcher()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f"Здравствуйте, <b>{message.from_user.full_name}!</b>\n"
                         f"Вас приветствует бот доставки cafesmile!")
    await start_register_user(message)


async def start_register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    if db_register_user(full_name, chat_id):
        await message.answer(text='Авторизация прошла успешно')
        await show_main_menu(message)
    else:
        await message.answer(text='Для связи с Вами нам нужен Ваш контактный номер',
                             reply_markup=share_phone_button())


@dp.message(F.contact)
async def update_user_info_finish_register(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    if db_create_user_cart(chat_id):
        await message.answer(text="Регистрация прошла успешно!")

    await show_main_menu(message)


async def show_main_menu(message: Message):
    await message.answer(text='Выберите направление',
                         reply_markup=generate_main_menu())


@dp.message(F.text == "🎯 Сделать заказ")
async def make_order(message: Message):
    chat_id = message.chat.id
    # TODO получить id корзины пользователя
    await bot.send_message(chat_id=chat_id,
                           text='Начнем',
                           reply_markup=back_to_main_menu())
    await message.answer(text="Выберите категорию",
                         reply_markup=generate_category_menu())


@dp.message(F.text.regexp(r'Г[а-я]+ [а-я]{4}'))
async def return_to_main_menu(message: Message):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await show_main_menu(message)


@dp.callback_query(F.data.regexp(r'category_[1-9]'))
async def show_product_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(text='Выберите продукт',
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=show_product_by_category(category_id))


@dp.callback_query(F.data == 'return_to_category')
async def return_to_category_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='Выберите категорию',
                                reply_markup=generate_category_menu())


@dp.callback_query(F.data.contains('product_'))
async def show_product_detail(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split('_')[-1])
    product = db_get_product_by_id(product_id)
    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)
    if user_cart := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart.id)
        text = text_for_caption(product.product_name, product.description, product.price)
        await bot.send_message(chat_id=chat_id,
                               text='Выберите модификатор',
                               reply_markup=back_arrow_button())

        await bot.send_photo(chat_id=chat_id,
                             photo=FSInputFile(path=product.image),
                             caption=text,
                             reply_markup=generate_constructor_button())

    else:
        await bot.send_message(chat_id=chat_id,
                               text="К сожалению у нас нет Вашего контакта",
                               reply_markup=share_phone_button())


@dp.message(F.text == '↩️Назад')
async def return_to_category_menu(message: Message):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await make_order(message)


@dp.callback_query(F.data.regexp(r'action [+-]'))
async def constructor_change(call: CallbackQuery):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    action = call.data.split()[-1]
    product_name = call.message.caption.split('\n')[0]
    user_cart = db_get_user_cart(chat_id)
    product = db_get_product_by_name(product_name)
    product_price = product.price

    match action:
        case '+':
            user_cart.total_products += 1
            product_price = product_price * user_cart.total_products
            db_update_to_cart(price=product_price,
                              quantity=user_cart.total_products,
                              cart_id=user_cart.id)
        case '-':
            if user_cart.total_products < 2:
                await call.answer('Mенее 1 товара выбрать нельзя')
            else:
                user_cart.total_products -= 1
            product_price = product_price * user_cart.total_products
            db_update_to_cart(price=product_price,
                              quantity=user_cart.total_products,
                              cart_id=user_cart.id)

    text = text_for_caption(name=product_name,
                            description=product.description,
                            price=product_price)
    try:
        await bot.edit_message_media(chat_id=chat_id,
                                     message_id=message_id,
                                     media=InputMediaPhoto(media=FSInputFile(path=product.image), caption=text),
                                     reply_markup=generate_constructor_button(user_cart.total_products))
    except TelegramBadRequest:
        pass


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
