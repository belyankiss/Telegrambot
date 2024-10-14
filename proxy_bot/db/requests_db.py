from datetime import datetime
from typing import Optional, Union, Dict, List

from aiogram.types import Message, CallbackQuery
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from proxy_bot.constants.msg_constants import ForAdminAfterRegistration, ShortButton
from proxy_bot.custom_sender.send_class import SendAdmins
from proxy_bot.db.create_async_session import async_session
from proxy_bot.db.models import User, Purchase
from proxy_bot.helpers import countries_dict


class BaseSession:
    def __init__(self):
        self.session = async_session


class UserRegistration(BaseSession):
    def __init__(self):
        super().__init__()
        self.to_admin = SendAdmins()

    async def new_user(self, session: AsyncSession, event: Union[Message, CallbackQuery]):
        date = datetime.now()
        referral_id = (int(event.text.split()[1]) if "/start " in event.text else None)
        if referral_id is not None and referral_id == event.from_user.id:
            referral_id = None
        user = User(user_id=event.from_user.id,
                    username=event.from_user.username,
                    date_registration=date,
                    referral_id=referral_id,
                    date_active=date)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        text = ForAdminAfterRegistration(username=event.from_user.username).text()
        await self.to_admin.to_all_admins(text)  # send message to all admins after registration user
        return user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        return await session.get(User, user_id)

    async def update_date_active(self, session: AsyncSession, user_id: int, username: Optional[str]) -> None:
        date = datetime.now()
        user = await self.get_user_by_id(session, user_id)
        if user:
            user.date_active = date
            user.username = username
            await session.commit()
            await session.refresh(user)


class UserProfile(BaseSession):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def get_info_user_for_profile(self) -> Dict:
        async with self.session() as session:
            referral_alias = aliased(User)

            stmt = (
                select(
                    User.username,
                    User.balance,
                    func.coalesce(func.count(Purchase.id), 0).label('purchase_count'),
                    func.coalesce(func.sum(User.referral_balance), 0).label('referral_income'),
                    func.coalesce(func.count(referral_alias.user_id), 0).label('referral_count')
                )
                .outerjoin(Purchase, Purchase.user_id.is_(User.user_id))
                .outerjoin(referral_alias,
                           referral_alias.referral_id.is_(User.user_id))  # Используем алиас для соединения
                .where(User.user_id.is_(self.user_id))
                .group_by(User.user_id)
            )

            result = await session.execute(stmt)
            summary = result.fetchone()
            return {
                'username': summary.username,
                'balance': summary.balance,
                'purchase_count': summary.purchase_count,
                'referral_income': summary.referral_income,
                'referral_count': summary.referral_count,
                'user_id': self.user_id
            }

    async def get_user_purchases(self) -> List[Optional[Purchase]]:
        async with self.session() as session:
            stmt = select(Purchase).where(Purchase.user_id.is_(self.user_id))
            return list(await session.scalars(stmt))

    async def get_one_purchase(self, purchase_id: int) -> dict:
        async with self.session() as session:
            result: Purchase = await session.scalar(select(Purchase).where(Purchase.id.is_(purchase_id)))
            product_name = getattr(ShortButton, result.product_type)
            if result.product_type == 'work':
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

    async def update_balance(self, amount: float):
        async with self.session() as session:
            user = await session.get(User, self.user_id)
            user.balance += round(amount, 2)
            await session.commit()
