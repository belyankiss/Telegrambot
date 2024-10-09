import asyncio

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship

from proxy_bot.db.create_async_session import async_engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    balance = Column(Float, nullable=False, default=0.0)
    blocked = Column(Boolean, default=False)
    date_registration = Column(DateTime, nullable=False)
    date_active = Column(DateTime)
    referral_id = Column(BigInteger, nullable=True)
    referral_balance = Column(Float, default=0)
    discount = Column(Float, nullable=True)
    activated_list = Column(String)

    purchases = relationship('Purchase', backref='buyer')

    def __repr__(self):
        return f'<User {self.user_id} | {self.username} | {self.balance} | {self.blocked}>'


class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    host = Column(String(50))
    port = Column(Integer)
    port_socks = Column(Integer, nullable=True, default=None)
    password = Column(String(50))
    username = Column(String(50))
    country = Column(String(20), nullable=True)
    city = Column(String(50), nullable=True)
    purchase_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=False)
    product_type = Column(String(20))  # Тип товара (work, scrolling)


class Admin(Base):
    __tablename__ = 'admins'

    user_id = Column(BigInteger, unique=True, primary_key=True)
    username = Column(String, nullable=True)


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    category = Column(String(20))
    href_photo = Column(String(500))


class Discount(Base):
    __tablename__ = 'discounts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    discount = Column(Float)
    activates = Column(Integer)


class ProxyWork(Base):
    __tablename__ = 'proxies'

    id = Column(Integer, primary_key=True)
    host = Column(String)
    port = Column(String)
    username = Column(String)
    password = Column(String)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    date = Column(String)
    used = Column(Integer)
    work = Column(Boolean, nullable=True)

    def __repr__(self):
        return f'{self.host}:{self.port}:{self.username}:{self.password} | {self.used} | {self.work}'


class ProxySort(Base):
    __tablename__ = 'proxies_sort'

    id = Column(Integer, primary_key=True)
    host = Column(String)
    port = Column(String)
    username = Column(String)
    password = Column(String)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    date = Column(String)
    used = Column(Integer)
    work = Column(Boolean, nullable=True)

    def __repr__(self):
        return f'{self.host}:{self.port}:{self.username}:{self.password} | {self.used} | {self.work}'



class DataProxy(Base):
    __tablename__ = 'data_proxies'

    id = Column(Integer, primary_key=True)  # ID прокси
    data = Column(String, nullable=True)  # Данные регистрации
    api_key = Column(String, nullable=True)
    username = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)


async def create_tables():
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    asyncio.run(create_tables())