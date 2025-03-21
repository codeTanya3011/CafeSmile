from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from telegramBotCafe.database.db_utils import (db_get_all_category, db_get_products,
                                               db_get_finally_price, db_get_product_for_delete)


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    categories = db_get_all_category()
    total_price = db_get_finally_price(chat_id)
    builder = InlineKeyboardBuilder()
    builder.button(text=f'🧺 Ваш кошик складає: {total_price if total_price else 0} UAH', callback_data='Ваш кошик')
    [builder.button(text=category.category_name,
                    callback_data=f'category_{category.id}') for category in categories]

    builder.adjust(1, 2)

    return builder.as_markup()


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    products = db_get_products(category_id)
    builder = InlineKeyboardBuilder()
    [builder.button(text=product.product_name,
                    callback_data=f"product_{product.id}") for product in products]
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text='🔙 Назад ', callback_data='return_to_category')
    )

    return builder.as_markup()


def generate_constructor_button(category_id=None, quantity=1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='➖', callback_data='action -')
    builder.button(text=str(quantity), callback_data=str(quantity))
    builder.button(text='➕', callback_data='action +')
    builder.button(text='Покласти в кошик 🧺', callback_data='put info cart')

    builder.adjust(3, 1)

    return builder.as_markup()


def generate_delete_product(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cart_products = db_get_product_for_delete(chat_id)
    builder.button(text='🚀 Оформити замовлення', callback_data='order_pay')
    for finally_cart_id, product_name in cart_products:
        builder.button(text=f'❌ {product_name}', callback_data=f'delete_{finally_cart_id}')

    builder.adjust(1)
    return builder.as_markup()
