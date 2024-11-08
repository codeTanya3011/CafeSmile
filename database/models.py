from os import getenv

from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, Session
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, MetaData, Integer, BigInteger, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
metadata = MetaData()

DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_ADDRESS = getenv('DB_ADDRESS')
DB_NAME = getenv('DB_NAME')

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}', echo_pool="debug")


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    carts: Mapped[int] = relationship('Carts', back_populates='user_cart')

    def __str__(self):
        return self.name


class Carts(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    total_price: Mapped[int] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)

    user_cart: Mapped[Users] = relationship(back_populates='carts')
    finally_id: Mapped[int] = relationship('Finally_carts', back_populates='user_cart')

    def __str__(self):
        return str(self.id)


class Finally_carts(Base):
    __tablename__ = 'finally_carts'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50))
    final_price: Mapped[int] = mapped_column(DECIMAL(12, 2))
    quantity: Mapped[int]

    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.id'))
    user_cart: Mapped[Carts] = relationship(back_populates='finally_id')

    __table_args__ = (UniqueConstraint('cart_id', 'product_name'),)

    def __str__(self):
        return str(self.id)


class Categories(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(20))

    products = relationship('Products', back_populates='product_category')

    def __str__(self):
        return self.category_name


class Products(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String[20], unique=True)
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String[100])
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    product_category: Mapped[Categories] = relationship(back_populates='products')


def main():
    Base.metadata.create_all(engine)
    # TODO Clear later, db in process
    categories = ('Лаваши', 'Донeры', 'Хот-доги', 'Десерты', 'Соусы', 'Напитки')
    products = (
        (1, 'Лаваш класик', 150, 'Мясо, сыр, тесто, овощи сезонные', 'media/lavash/lavash1.jfif'),
        (1, 'Лаваш веганский', 75, 'Сыр, грибы, тесто, овощи сезонные', 'media/lavash/lavash3.png'),
        (1, 'Лаваш с морепродуктами', 200, 'Рыба/креветки, пармезан, тесто, огурец, перец',
         'media/lavash/lavash2jpg.jpg'),
        (1, 'Лаваш армянский с сыром', 200, 'Тесто, сыр, зелень, специи', 'media/lavash/lavash4jpg.jpg'),
        (2, 'Донер с курицей', 125, 'Курица, сыр, тесто, помидор, лук', 'media/doner/doner1.jpg'),
        (2, 'Донер с жареным тофу', 100, 'Тофу, тесто, овощи сезонные', 'media/doner/doner2.png'),
        (2, 'Донер царский', 200, 'Мясо, сыр, грибы, тесто, овощи сезонные, зелень', 'media/doner/doner3.jpg'),
        (2, 'Донер-кебаб', 150, 'Мясо, тесто, овощи сезонные, зелень, салат', 'media/doner/doner4.jpg'),
        (2, 'Донер домашний', 200, 'Мясо, орурец маринованый, помидор, тесто, зелень', 'media/doner/doner5.jpg'),
        (3, 'Хот-дог класик', 100, 'Сосиска, булочка, соусы', 'media/hot-dog/hot-dog1.jpg'),
        (3, 'Хот-дог царский', 150, 'Сосиска, булочка, сыр, соусы, овощи сезонные', 'media/hot-dog/hot-dog2.jpeg'),
        (4, 'Панна-котта с малиной', 75, 'Молоко, мука, желатин, какао, малина', 'media/desert/desert1.jpg'),
        (4, 'Пирожное битое стекло с фруктами', 50, 'Йогурт, желатин, фрукты сезонные', 'media/desert/desert2.jpg'),
        (4, 'Торт-мороженое с голубикой', 100, 'Бисквитные крошки, мороженое, голубика', 'media/desert/desert3.jpg'),
        (4, 'Тирамису с фруктами', 125, 'Печенье Савоярди, маскарпоне, кофе, сливки, какао, сезонные фрукты',
         'media/desert/desert4.jpg'),
        (4, 'Брауни с муссом из смородины', 100, 'Мука, какао, сметана, желатин, яйца, смородина',
         'media/desert/desert5.jpg'),
        (5, 'Медовая горчица', 25, 'Горчица, мед, соль, стабилизотор', 'media/sous/sous1.jpg'),
        (5, 'Барбекю', 25, 'Томатная паста, смесь перцев, зелень, соль', 'media/sous/sous2.jpg'),
        (5, 'Кисло-сладкий', 25, 'Томатная паста, острый перец, часнок, имбирь, мед, соль, стабилизотор',
         'media/sous/sous3.png'),
        (5, 'Соусы на выбор классические', 20, 'Часночный, сырный, кетчуп, майонез, тар-тар', 'media/sous/sous4.png'),
        (6, 'Клубничное мохито', 100, 'Газировка, мята, клубника, сахар, лайм', 'media/sweetwater/sweetwater1.jpg'),
        (6, 'Лимонад класик', 75, 'Газировка, сахар, лимон, апельсин, мята', 'media/sweetwater/sweetwater2.jpg'),
        (6, 'Ром-кола', 150, 'Кола, ром, мякоть апельсина, розмарин', 'media/sweetwater/sweetwater3.jpeg'),
        (6, 'Чай в ассортименте', 35, 'Смородина, эхинацея, облипиха, зеленый, черный, каркаде, с молоком, матча',
         'media/sweetwater/sweetwater4.png'),
        (6, 'Кофе в ассортименте', 50, 'Фраппе, латте, капучино, американо, какао', 'media/sweetwater/sweetwater5.jpg'),
        (6, 'Напитки на выбор', 30, 'Минеральная вода, кола, фанта, соки в ассортименте, спрайт',
         'media/sweetwater/sweetwater6.jfif'),
    )

    with Session(engine) as session:
        for category in categories:
            query = Categories(category_name=category)
            session.add(query)
            session.commit()

        for product in products:
            query = Products(
                category_id=product[0],
                product_name=product[1],
                price=product[2],
                description=product[3],
                image=product[4]
            )
            session.add(query)
            session.commit()


if __name__ == '__main__':
    main()
