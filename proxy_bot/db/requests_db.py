from datetime import datetime
from typing import Optional, Union, List, Tuple

from aiogram.types import Message, CallbackQuery
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from proxy_bot.constants.msg_constants import ForAdminAfterRegistration, ShortButton
from proxy_bot.custom_sender.send_class import SendAdmins
from proxy_bot.db.create_async_session import async_session
from proxy_bot.db.models import User, Purchase, Discount, Admin, ProxyWork, Photo, ProxySort
from proxy_bot.helpers import countries_dict


class BaseSession:
    def __init__(self):
        self.session = async_session


class UserORM(BaseSession):
    def __init__(self,
                 event: Optional[Union[Message, CallbackQuery]] = None,
                 user_id: Optional[int] = None,
                 username: Optional[str] = None):
        super().__init__()
        self.user_id: int = event.from_user.id if event is not None else user_id
        self.username: Optional[str] = event.from_user.username if event is not None else username
        if isinstance(event, Message):
            self.referral_id: Optional[int] = (int(event.text.split()[1]) if "/start " in event.text else None)
        else:
            self.referral_id = None
        self.date = datetime.now()

        self.purchases = PurchaseORM(self.user_id) if self.user_id is not None else None

    async def is_exist_user(self, session: AsyncSession) -> Optional[User]:
        return await session.get(User, self.user_id)

    async def _update_date_username_active(self, session: AsyncSession, user: User):
        updated = False
        if user.date_active != self.date:
            user.date_active = self.date
            updated = True
        if user.username != self.username:
            user.username = self.username
            updated = True
        if updated:
            await session.commit()

    async def _add_user(self, session: AsyncSession):
        user = User(user_id=self.user_id,
                    username=self.username,
                    date_registration=self.date,
                    referral_id=self.referral_id,
                    date_active=self.date)
        session.add(user)
        await session.commit()

    async def create_user(self):
        async with self.session() as session:
            user = await self.is_exist_user(session)
            if user is not None:
                await self._update_date_username_active(session, user)
            else:
                await self._add_user(session)
                await SendAdmins().to_all_admins(ForAdminAfterRegistration(username=self.username).text)

    async def is_blocked_user(self) -> bool:
        async with self.session() as session:
            user = await self.is_exist_user(session)
            if user is not None:
                return user.blocked
            return False

    async def _get_referral_count(self, session: AsyncSession) -> Tuple[int, int]:
        stmt = select(User.referral_balance).where(User.referral_id.is_(self.user_id))
        balances = list(await session.scalars(stmt))
        return len(balances), sum(balances) if balances else 0

    async def _count_user_purchases(self, session: AsyncSession) -> int:
        return await self.purchases.get_purchase_count(session)

    async def user_profile_info(self) -> dict:
        async with self.session() as session:
            user: User = await self.is_exist_user(session)
            referral_count, referral_income = await self._get_referral_count(session)
            return {
                'username': self.username,
                'balance': user.balance,
                'purchase_count': await self._count_user_purchases(session),
                'referral_income': referral_income,
                'referral_count': referral_count,
                'user_id': self.user_id
            }

    async def get_user_purchases(self):
        async with self.session() as session:
            return await self.purchases.get_user_purchases(session)

    async def get_one_purchase(self, purchase_id: int):
        async with self.session() as session:
            return await self.purchases.get_one_purchase(session, purchase_id)

    async def update_balance(self, amount: float):
        async with self.session() as session:
            user = await session.get(User, self.user_id)
            user.balance += round(amount, 2)
            await session.commit()

    async def save_discount(self, discount: float, name_discount: str):
        async with self.session() as session:
            user = await self.is_exist_user(session)
            user.discount = discount
            if user.activated_list is None:
                user.activated_list = f"{name_discount},"
            else:
                user.activated_list += f"{name_discount},"
            await session.commit()

    async def minus_balance(self, price: Union[int, float]) -> User:
        async with self.session() as session:
            user = await self.is_exist_user(session)
            user.balance -= price
            await session.commit()
            await session.refresh(user)
            return user



class PurchaseORM:
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def get_purchase_count(self, session: AsyncSession) -> int:
        stmt = select(func.count(Purchase.id)).filter(Purchase.user_id.is_(self.user_id))
        result = await session.scalar(stmt)
        return result

    async def get_user_purchases(self, session: AsyncSession) -> List[Optional[Purchase]]:
        stmt = select(Purchase).where(Purchase.user_id.is_(self.user_id))
        return list(await session.scalars(stmt))

    @staticmethod
    async def get_one_purchase(session: AsyncSession, purchase_id: int) -> dict:
        result: Purchase = await session.scalar(select(Purchase).where(Purchase.id.is_(purchase_id)))
        product_name = getattr(ShortButton, result.product_type)
        if result.product_type == 'work' or result.product_type == 'sort':
            data = {
                "product_name": product_name,
                "amount": result.amount,
                "country": countries_dict(result.country),
                "city": result.city,
                "host": result.host,
                "port": result.port,
                "username": result.username,
                "password": result.password,
            }

        else:
            data = {
                "product_name": product_name,
                "amount": result.amount,
                "country": countries_dict(result.country),
                "purchase_time": result.purchase_time.strftime("%d-%m-%Y %H:%M"),
                "end_time": result.end_time.strftime("%d-%m-%Y %H:%M"),
                "host": result.host,
                "port": result.port,
                "port_socks": result.port_socks,
                "username": result.username,
                "password": result.password,
            }

        return data

    async def save_purchase(self, proxy: Union[ProxyWork, ProxySort], amount: int):
        async with async_session() as session:
            purchase_time = datetime.now()
            end_time = None
            port_socks = None
            if isinstance(proxy, ProxySort):
                product_type = "sort"
            else:
                product_type = "work"
            purchase = Purchase(user_id=self.user_id,
                                host=proxy.host,
                                port=proxy.port,
                                port_socks=port_socks,
                                password=proxy.password,
                                username=proxy.username,
                                country=proxy.country,
                                city=proxy.city,
                                purchase_time=purchase_time,
                                end_time=end_time,
                                amount=amount,
                                product_type=product_type
                                )
            session.add(purchase)
            await session.commit()

    @staticmethod
    async def save_proxyline_purchase(proxy: Purchase):
        async with async_session() as session:
            session.add(proxy)
            await session.commit()




class DiscountORM(BaseSession):
    def __init__(self):
        super().__init__()

    async def get_discounts(self, name: str) -> Optional[Discount]:
        async with self.session() as session:
            return await session.scalar(select(Discount).where(Discount.name.is_(name)))

    async def change_discount_count(self, name: str):
        async with self.session() as session:
            discount = await session.scalar(select(Discount).where(Discount.name.is_(name)))
            discount.activates -= 1
            await session.commit()


class Proxies(BaseSession):
    def __init__(self, tablename: str):
        super().__init__()
        if tablename == "ProxyWork":
            self.table = ProxyWork
        else:
            self.table = ProxySort

    async def get_proxies(self):
        async with self.session() as session:
            return list(await session.scalars(select(self.table)
                                              .where(self.table.work.is_(True) & self.table.used.is_(False))))

    async def update_busy_proxy(self, proxy_id: int):
        async with self.session() as session:
            await session.execute(update(self.table).where(self.table.id.is_(proxy_id)).values(used=True))
            await session.commit()

    async def get_bad_proxy(self):
        async with self.session() as session:
            work = list(await session.scalars(select(ProxyWork).where(ProxyWork.work.is_(False))))
            sort = list(await session.scalars(select(ProxySort).where(ProxySort.work.is_(False))))
            return work, sort

    async def add_bad_proxy(self, proxy_id: int):
        async with self.session() as session:
            await session.execute(update(self.table).where(self.table.id.is_(proxy_id)).values(work=False))
            await session.commit()

    async def kill_proxy(self):
        async with self.session() as session:
            await session.execute(update(self.table).values(work=False))
            await session.commit()



class AdminsORM:
    @staticmethod
    async def get_admins():
        async with async_session() as session:
            return await session.scalars(select(Admin.user_id))


async def load_photos():
    async with async_session() as session:
        return list(await session.scalars(select(Photo)))
