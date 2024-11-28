from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup


def share_phone_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="☎️Надіслати свій контакт📞", request_contact=True)

    return builder.as_markup(resize_keyboard=True)


def generate_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Зробити замовлення")
    builder.button(text="🎯🏇🏼 Геолокація та доставка")
    builder.button(text="🧺 Кошик")
    builder.button(text="⚙️ Налаштування")
    builder.adjust(2, 2)

    return builder.as_markup(resize_keyboard=True)


def delivery_and_pickup() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚛 Доставка")
    builder.button(text="🚴🏼‍♂️ Самовивіз")
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def back_to_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="✨ Головне меню")

    return builder.as_markup(resize_keyboard=True)


def back_arrow_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="↩️ До кошика")

    return builder.as_markup(resize_keyboard=True)