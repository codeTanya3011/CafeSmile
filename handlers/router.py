from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.models import Categories, Products, engine
from sqlalchemy.orm import Session

router = Router()  # Создаем экземпляр роутера

#
# # Обработчик для добавления категории
# @router.message(F.text == "➕ Добавить категорию")
# async def ask_category_name(message: Message):
#     await message.answer("Введите название категории:")
#
#
# # Обработчик для добавления категории в БД
# @router.message()
# async def add_category(message: Message):
#     category_name = message.text
#
#     # Используем with Session(engine) как в примере
#     with Session(engine) as session:  # Создаем сессию с использованием Session(engine)
#         category = Categories(category_name=category_name)
#         session.add(category)
#         session.commit()
#
#     await message.answer(f"Категория '{category_name}' добавлена!")
#
#
# # Обработчик для добавления товара
# @router.message(Command("add_product"))
# async def add_product(message: Message):
#     args = message.text.split(maxsplit=4)
#     if len(args) < 5:
#         await message.answer("Использование: /add_product Название Описание Цена КатегорияID")
#         return
#
#     name, description, price, category_id = args[1], args[2], float(args[3]), int(args[4])
#
#     with Session(engine) as session:  # Создаем сессию с использованием Session(engine)
#         product = Products(product_name=name, description=description, price=price, category_id=category_id)
#         session.add(product)
#         session.commit()
#
#     await message.answer(f"Товар '{name}' добавлен!")
#
#
# # Обработчик для списка категорий
# @router.message(Command("list_categories"))
# async def list_categories(message: Message):
#     with Session(engine) as session:  # Создаем сессию с использованием Session(engine)
#         categories = session.query(Categories).all()
#
#     if not categories:
#         await message.answer("Категорий пока нет.")
#         return
#
#     category_list = "\n".join([f"{cat.id}: {cat.category_name}" for cat in categories])
#     await message.answer(f"Список категорий:\n{category_list}")
