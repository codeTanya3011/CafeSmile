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
    phone: Mapped[str] = mapped_column(String(15), nullable=True)

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
    finally_id: Mapped[int] = relationship('FinallyCarts', back_populates='user_cart')

    def __str__(self):
        return str(self.id)


class FinallyCarts(Base):
    __tablename__ = 'finally_carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100))
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
    category_name: Mapped[str] = mapped_column(String(100))

    products = relationship('Products', back_populates='product_category')

    def __str__(self):
        return self.category_name


class Products(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String[100], unique=True)
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String[100])
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    product_category: Mapped[Categories] = relationship(back_populates='products')


# TODO: Добавить мультиязычность
# class Languages(Base):
#    __language__ = 'languages'