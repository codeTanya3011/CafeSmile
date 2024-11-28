from database.db_utils import db_get_FinallyCart_products


def text_for_caption(name, description, price):
    text = f'<b>{name}</b>\n\n'
    text += f'<b>Ингредиенты:</b> {description}\n'
    text += f'<b>Цена:</b> {price}'

    return text


def counting_products_from_cart(chat_id, user_text):
    products = db_get_FinallyCart_products(chat_id)
    if products:
        text = f'{user_text}\n\n'
        total_products = total_price = count = 0
        for name, quantity, price, cart_id in products:
            count += 1
            total_products += quantity
            total_price += price
            text += f'{count}. {name}\nКоличество: {quantity}\nСтоимость: {price}\n\n'

        text += f'Общее количество продуктов: {total_products}\nОбщая стоимость корзины: {total_price}'

        context = (count, text, total_price, chat_id)
        return context
