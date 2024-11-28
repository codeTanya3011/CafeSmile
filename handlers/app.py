from os import getenv

from aiogram import Bot, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, LabeledPrice, KeyboardButton
from dotenv import load_dotenv

from database.db_utils import *
from keyboards.inline_kb import *
from keyboards.reply_kb import *
from utils.caption import *

load_dotenv()
TOKEN = getenv('TOKEN')
PAY = getenv('PORTMONE')
MANAGER = getenv('MANAGER')
router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

LANGUAGES = {
    "🇬🇧 English": "en",
    "🇷🇺 Русский": "ru",
    "🇺🇦 Українська": "uk"
}
user_language = {}  # TODO Хранилище языков пользователей (можно заменить на базу данных)


@router.message(F.text == "⚙️ Настройки")
async def start_handler(message: Message):
    buttons = [[KeyboardButton(text=lang)] for lang in LANGUAGES.keys()]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Выберите язык / Choose your language / Оберіть мову:", reply_markup=keyboard)


@router.message(F.text.in_(LANGUAGES.keys()))
async def set_language_handler(message: Message):
    user_id = message.chat.id
    selected_language = LANGUAGES[message.text]  # Получаем код языка (en, ru, uk)
    user_language[user_id] = selected_language  # Сохраняем выбор пользователя

    if selected_language == "en":
        await message.answer("Language set to English. Let's get started!")
    elif selected_language == "ru":
        await message.answer("Язык установлен на русский. Начнем!")
    elif selected_language == "uk":
        await message.answer("Мова встановлена на українську. Розпочнемо!")

    await show_main_menu(message)


@router.message(CommandStart())
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


@router.message(F.contact)
async def update_user_info_finish_register(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    if db_create_user_cart(chat_id):
        await message.answer(text="Регистрация прошла успешно!")

    await show_main_menu(message)


@router.message(F.text == "🚚 Геолокация и доставка")
async def start_handler(message: Message):
    # Создаем кнопки "Доставка" и "Самовывоз"
    delivery_button = KeyboardButton(text="🚚 Доставка")
    pickup_button = KeyboardButton(text="🏠 Самовывоз")
    keyboard = ReplyKeyboardMarkup(keyboard=[[delivery_button, pickup_button]], resize_keyboard=True)

    await message.answer("Выберите способ получения:", reply_markup=keyboard)


@router.message(F.text == "🚚 Доставка")
async def delivery_handler(message: Message):
    location_button = KeyboardButton(text="Отправить геолокацию", request_location=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[location_button]], resize_keyboard=True)

    await message.answer(text="Вы выбрали доставку\n"
                              "Пожалуйста, отправьте вашу геолокацию для расчета (не забудьте включить местоположение на телефоне)",
                         reply_markup=keyboard)


@router.message(F.text == "🏠 Самовывоз")
async def pickup_handler(message: Message):
    await message.answer(text="Вы выбрали самовывоз\n"
                              "Наш адрес: ул. Примерная, д. 123\n"
                              "Оплатите пожалуйста покупку, а мы будем вас ждать!",
                         reply_markup=back_to_main_menu())


@router.message(lambda message: message.location is not None)
async def location_handler(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    await message.answer(f"Спасибо! Ваша геолокация получена:\nШирота: {latitude}\nДолгота: {longitude}")
    await message.answer(text="Доставка будет рассчитана в ближайшее время. Ожидайте!")
    await message.answer(text="Доставка выходит 100 UAH\n"
                              "Если вас устраивает, оплатите пожалуйста покупку и ожидайте доставку в течении часа",
                         reply_markup=back_to_main_menu())


async def show_main_menu(message: Message):
    await message.answer(text='Выберите направление',
                         reply_markup=generate_main_menu())


@router.message(F.text == "🎯 Сделать заказ")
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id,
                           text='Начнем',
                           reply_markup=back_to_main_menu())
    await message.answer(text="Выберите категорию",
                         reply_markup=generate_category_menu(chat_id))


@router.message(F.text.regexp(r'Г[а-я]+ [а-я]{4}'))
async def return_to_main_menu(message: Message):
    try:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id - 1)
    except TelegramBadRequest:
        ...
    await show_main_menu(message)


@router.callback_query(F.data.regexp(r'category_[1-9]'))
async def show_product_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(text='Выберите продукт',
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=show_product_by_category(category_id))


@router.callback_query(F.data == 'return_to_category')
async def return_to_category_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='Выберите категорию',
                                reply_markup=generate_category_menu(chat_id))


@router.callback_query(F.data.contains('product_'))
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


@router.message(F.text == '↩️Назад')
async def return_to_category_menu(message: Message):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await make_order(message)


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
                               text='Продукт успешно добавлен ☑️')
    else:
        await bot.send_message(chat_id=chat_id,
                               text='Количество успешно изменено ✏️')

    await return_to_category_menu(call.message)


@router.callback_query(F.data == 'Ваша корзина')
async def show_finally_cart(call: CallbackQuery):
    """Показ содержимого корзины"""
    message_id = call.message.message_id
    chat_id = call.from_user.id
    await bot.delete_message(chat_id=chat_id,
                             message_id=call.message.message_id)
    context = counting_products_from_cart(chat_id, 'Ваша корзина:')
    if context:
        count, text, *_ = context
        await bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=generate_delete_product(chat_id))
    else:
        await bot.send_message(chat_id=chat_id,
                               text='Ваша корзина пуста😱')
        await make_order(call.message)


@router.callback_query(F.data.regexp(r'delete_\d+'))
async def delete_cart_product(call: CallbackQuery):
    """ Delete buttons ❌"""
    finally_id = int(call.data.split('_')[-1])
    db_delete_product(finally_id)
    await bot.answer_callback_query(callback_query_id=call.id,
                                    text='Продукт удален с корзины!')
    await show_finally_cart(call)


@router.callback_query(F.data == 'order_pay')
async def create_order(call: CallbackQuery):
    """Оплата товаров (тестовая)"""
    chat_id = call.from_user.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)

    count, text, total_price, cart_id = counting_products_from_cart(chat_id=chat_id,
                                                                    user_text='Оплата заказа:')
    text += "\nДоставка по городу 100 UAH"

    await bot.send_invoice(chat_id=chat_id,
                           title='Ваш заказ:',
                           description=text,
                           payload='bot-defined invoice payload',
                           provider_token=PAY,
                           currency='UAH',
                           prices=[
                               LabeledPrice(label='Общая стоимость', amount=int(total_price) * 100),
                               LabeledPrice(label='Доставка', amount=100 * 100)
                           ])

    await bot.send_message(chat_id=chat_id,
                           text='Заказ оплачен. Спасибо!')
    await sending_report_to_manager(chat_id, text)

    clear_finally_cart(cart_id)


async def sending_report_to_manager(chat_id: int, text: str):
    """Отправка заказов в чат группы"""
    user = db_get_user_info(chat_id)
    text += f'\n\nИмя клиента: {user.name}\nКонтакт: {user.phone}\n\n'
    await bot.send_message(chat_id=MANAGER,
                           text=text)


@router.message(F.text == '🧺 Корзина')
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id,
                           text='Начнем',
                           reply_markup=back_to_main_menu())
    context = counting_products_from_cart(chat_id, 'Ваша корзина:')
    if context:
        count, text, *_ = context
        await bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=generate_delete_product(chat_id))
    else:
        await bot.send_message(chat_id=chat_id,
                               text='Ваша корзина пуста😱')
        await make_order(message)
