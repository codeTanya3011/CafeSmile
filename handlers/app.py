import os
import asyncio
from os import getenv

from pathlib import Path
from aiogram import Bot, F, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, LabeledPrice, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

from telegramBotCafe.database.db_utils import *
from telegramBotCafe.keyboards.inline_kb import *
from telegramBotCafe.keyboards.reply_kb import *
from telegramBotCafe.utils.caption import *


load_dotenv()

MEDIA_PATH = Path(getenv("MEDIA_PATH")).resolve()

TOKEN = getenv('TOKEN')
PAY = getenv('PORTMONE')
MANAGER = getenv('MANAGER')
router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

LANGUAGES = {
    "🇬🇧 English": "en",
    "🇺🇦 Українська": "uk"
}
user_language = {}  # TODO Хранилище языков пользователей


def get_image_path(image_name):
    return MEDIA_PATH / image_name


@router.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f"Добрий день, <b>{message.from_user.full_name}!</b>\n"
                         f"вас вітає бот cafesmile!")
    await start_register_user(message)


@router.message(F.text == "⚙️ Налаштування")
async def start_handler(message: Message):
    buttons = [[KeyboardButton(text=lang)] for lang in LANGUAGES.keys()]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Оберіть мову / Choose your language:", reply_markup=keyboard)


@router.message(F.text.in_(LANGUAGES.keys()))
async def set_language_handler(message: Message):
    user_id = message.chat.id
    selected_language = LANGUAGES[message.text]
    user_language[user_id] = selected_language

    if selected_language == "en":
        await message.answer("Language set to English. Let's get started!")
    elif selected_language == "uk":
        await message.answer("Мова встановлена на українську. Розпочнемо!")

    await show_main_menu(message)


async def start_register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    if db_register_user(full_name, chat_id):
        await message.answer(text='Авторизація пройшла успішно')
        await show_main_menu(message)
    else:
        await message.answer(text="Для зв'язку з Вами нам потрібний Ваш контактний номер",
                             reply_markup=share_phone_button())


@router.message(F.contact)
async def update_user_info_finish_register(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    if db_create_user_cart(chat_id):
        await message.answer(text="Регістрація пройшла успішно!")

    await show_main_menu(message)


@router.message(F.text == "🎯🏇🏼 Геолокація та доставка")
async def start_handler(message: Message):
    # Создаем кнопки "Доставка" и "Самовывоз"
    delivery_button = KeyboardButton(text="🚛 Доставка")
    pickup_button = KeyboardButton(text="🚴🏼‍♂️ Самовивіз")
    keyboard = ReplyKeyboardMarkup(keyboard=[[delivery_button, pickup_button]], resize_keyboard=True)

    await message.answer("Виберіть спосіб отримання:", reply_markup=keyboard)


@router.message(F.text == "🚛 Доставка")
async def delivery_handler(message: Message):
    location_button = KeyboardButton(text="Відправити геолокацію", request_location=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[location_button]], resize_keyboard=True)

    await message.answer(text="Ви обрали доставку\n"
                              "Будь ласка, надішліть вашу геолокацію для розрахунку (не забудьте увімкнути місцезнаходження на телефоні)",
                         reply_markup=keyboard)


@router.message(F.text == "🚴🏼‍♂️ Самовивіз")
async def pickup_handler(message: Message):
    await message.answer(text="Ви обрали самовивіз\n"
                              "Наша адреса: вул. Мирна, буд. 23\n"
                              "Оплатіть будь ласка покупку, а ми будемо на вас чекати!",
                         reply_markup=back_to_main_menu())


@router.message(lambda message: message.location is not None)
async def location_handler(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    await message.answer(f"Дякую! Вашу геолокацію отримано:\nШирота: {latitude}\nДовгота: {longitude}")
    await message.answer(text="Доставка буде розрахована найближчим часом❤️‍🔥Чекайте!")
    # Ожидание 5 секунд перед следующим сообщением
    await asyncio.sleep(9)
    await message.answer(text="Доставка виходить 100 UAH по місту🍾\n"
                              "Якщо вас влаштовує, сплатіть будь-ласка покупку та чекайте на доставку протягом години🍽\n"
                              "Для уточнення по замовленню вам може подзвонити наш менеджер🤙\nГарного вам дня та до зустрічі🫰",
                         reply_markup=back_to_main_menu())


async def show_main_menu(message: Message):
    await message.answer(text='🔁 Виберіть напрямок',
                         reply_markup=generate_main_menu())


@router.message(F.text == "✅ Зробити замовлення")
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id,
                           text='🪄 Розпочнемо',
                           reply_markup=back_to_main_menu())
    await message.answer(text="📋 Виберіть категорію",
                         reply_markup=generate_category_menu(chat_id))


@router.message(F.text.regexp(r'Г[а-я]+ [а-я]{4}'))
async def return_to_main_menu(message: Message):
    try:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id - 1)
    except TelegramBadRequest:
        ...
    await show_main_menu(message)


@router.callback_query(F.data.regexp(r'category_[1-15]'))
async def show_product_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(text='🥢 Виберіть продукт',
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=show_product_by_category(category_id))


@router.callback_query(F.data == 'return_to_category')
async def return_to_category_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='🍎 Виберіть категорію',
                                reply_markup=generate_category_menu(chat_id))


@router.callback_query(F.data.contains('product_'))
async def show_product_detail(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split('_')[-1])

    # Получаем продукт из базы данных
    product = db_get_product_by_id(product_id)

    # Проверяем, существует ли товар
    if not product:
        await bot.send_message(chat_id=chat_id, text="❌ Помилка: товар не знайдено!")
        return

    # Получаем категорию через связь product_category
    category = product.product_category
    category_id = category.id if category else None  # Получаем id категории

    image_path = get_image_path(product.image)

    # Проверяем, существует ли файл
    if not os.path.exists(image_path):
        print(f"Помилка: файл {image_path} не знайдено!")  # Лог в консоли
        await bot.send_message(chat_id=chat_id, text="Помилка: зображення товару не знайдено!")
        return

    # class UserState(StatesGroup):
    #     step1 = State()  # Первый шаг
    #     step2 = State()  # Второй шаг

    # # Создаем кнопку "Назад"
    # back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_previous_step")

    # # Создаем разметку для кнопки "Назад" в инлайн-клавиатуре
    # back_button_markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    # # Удаляем прошлое сообщение

    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)
    if user_cart := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart.id)
        category_id = int(call.data.split('_')[-1])
        text = text_for_caption(product.product_name, product.description, product.price)
        await bot.send_message(chat_id=chat_id,
                               text="🍐 Оберіть товар",
                               reply_markup=generate_category_menu(chat_id))
        await bot.send_photo(chat_id=chat_id,
                             photo=FSInputFile(str(image_path)),
                            #  media=InputMediaPhoto(media=FSInputFile(path=product.image), caption=text),
                             caption=text,
                             reply_markup=generate_constructor_button(category_id))  # Передаём категорию!

    else:
        await bot.send_message(chat_id=chat_id,
                               text="😿 На жаль, у нас немає Вашого контакту",
                               reply_markup=share_phone_button())


# @router.callback_query(F.data == "back_to_previous_step")
# async def back_to_previous_step(call: CallbackQuery, state: FSMContext):
#     """ Возвращаем на предыдущий шаг """
#     user_state = await state.get_state()

#     if user_state == "UserState.step2":
#         # Переход на шаг 1
#         await call.message.answer("Вы вернулись к шагу 1.", reply_markup=back_button_markup)
#         await state.set_state("UserState.step1")  # Переход к шагу 1

#     elif user_state == "UserState.step1":
#         # Уже на шаге 1, ничего не делаем или отправляем сообщение
#         await call.message.answer("Вы уже на шаге 1.", reply_markup=back_button_markup)

#     # Ответ на callback_query
#     await call.answer()


# @router.callback_query(F.data == 'back_to_products')
# async def back_to_products_button(call: CallbackQuery):
#     chat_id = call.message.chat.id
    
#     # Отправляем новое сообщение с выбором товаров или нужной категории
#     await bot.send_message(
#         chat_id=chat_id,
#         text="Оберіть товар",  # Или другой текст, который вам нужен
#         reply_markup=show_product_by_category(chat_id))  # Функция, возвращающая кнопки для выбора товаров


# @router.message(F.text == '↩️Назад')
# async def return_to_category_menu(message: Message):
#     await bot.delete_message(message.chat.id, message.message_id - 1)
#     await make_order(message)


@router.callback_query(F.data.regexp(r'action [+-]'))
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
                await call.answer('❗️ Менше 1 товару вибрати не можна')
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


@router.callback_query(F.data == 'put info cart')
async def put_info_cart(call: CallbackQuery):
    """Добавление товара в корзину"""
    chat_id = call.from_user.id
    product_name = call.message.caption.split('\n')[0]
    cart = db_get_user_cart(chat_id)

    await bot.delete_message(chat_id=chat_id,
                             message_id=call.message.message_id)
    if db_ins_or_upd_finally_cart(cart_id=cart.id,
                                  product_name=product_name,
                                  total_products=cart.total_products,
                                  total_price=cart.total_price):
        await bot.send_message(chat_id=chat_id,
                               text='☑️ Продукт успішно доданий')
    else:
        await bot.send_message(chat_id=chat_id,
                               text='✏️ Кількість успішно змінено')

    await generate_category_menu(call.message)


@router.callback_query(F.data == 'Ваш кошик')
async def show_finally_cart(call: CallbackQuery):
    """Показ содержимого корзины"""
    message_id = call.message.message_id
    chat_id = call.from_user.id
    await bot.delete_message(chat_id=chat_id,
                             message_id=call.message.message_id)
    context = counting_products_from_cart(chat_id, '🧺 Ваш кошик:')
    if context:
        count, text, *_ = context
        await bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=generate_delete_product(chat_id))
    else:
        await bot.send_message(chat_id=chat_id,
                               text='😱 Ваш кошик порожній')
        await make_order(call.message)


@router.callback_query(F.data.regexp(r'delete_\d+'))
async def delete_cart_product(call: CallbackQuery):
    """ Delete buttons ❌"""
    finally_id = int(call.data.split('_')[-1])
    db_delete_product(finally_id)
    await bot.answer_callback_query(callback_query_id=call.id,
                                    text='Продукт видалено з кошика❗️')
    await show_finally_cart(call)


@router.callback_query(F.data == 'order_pay')
async def create_order(call: CallbackQuery):
    """Оплата товаров (тестовая)"""
    chat_id = call.from_user.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)

    count, text, total_price, cart_id = counting_products_from_cart(chat_id=chat_id,
                                                                    user_text='🧮 Оплата замовлення:')
    text += "\n💰 Доставка по місту 100 UAH"

    await bot.send_invoice(chat_id=chat_id,
                           title='Ваше замовлення:',
                           description=text,
                           payload='bot-defined invoice payload',
                           provider_token=PAY,
                           currency='UAH',
                           prices=[
                               LabeledPrice(label='🧮 Загальна вартість', amount=int(total_price) * 100),
                               LabeledPrice(label='Доставка', amount=100 * 100)
                           ])

    # Отправляем отчет менеджеру (без очистки корзины на этом этапе)
    await sending_report_to_manager(chat_id, text)


@router.message(F.successful_payment)
async def payment_successful(message: Message):
    """Обработчик успешной оплаты"""
    chat_id = message.from_user.id

    try:
        clear_finally_cart(chat_id)  # Очищаем корзину по ID пользователя
        await message.answer("Дякую за вашу оплату❗️ Замовлення оформлене, кошик очищений")
    except Exception as e:
        await message.answer(f"Помилка під час очищення кошика: {e}")


async def sending_report_to_manager(chat_id: int, text: str):
    """Отправка заказов в чат группы"""
    user = db_get_user_info(chat_id)
    text += f"\n\nІм'я клієнта: {user.name}\nКонтакт: {user.phone}\n\n"
    await bot.send_message(chat_id=MANAGER,
                           text=text)


@router.message(F.text == '🧺 Кошик')
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id,
                           text='Почнемо',
                           reply_markup=back_to_main_menu())
    context = counting_products_from_cart(chat_id, '🧺 Ваш кошик:')
    if context:
        count, text, *_ = context
        await bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=generate_delete_product(chat_id))
    else:
        await bot.send_message(chat_id=chat_id, text='😱 Ваш кошик порожній')

