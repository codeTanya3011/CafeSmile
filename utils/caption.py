def text_for_caption(name, description, price):
    text = f'<b>{name}</b>\n\n'
    text += f'<b>Ингредиенты</b> {description}\n'
    text += f'<b>Цена:</b> {price}'

    return text
