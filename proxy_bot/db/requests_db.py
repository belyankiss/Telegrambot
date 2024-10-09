from datetime import datetime
from typing import Optional

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from proxy_bot.db.create_async_session import async_session
from proxy_bot.db.models import User


# class NewUser:
#
#     @staticmethod
#     async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
#         return await session.get(User, user_id)
#
#     @staticmethod
#     async def add_user(session: AsyncSession, user_id: int, username: Optional[str], date: datetime) -> User:
#         user = User(user_id=user_id,
#                     username=username,
#                     date_registration=date,
#                     date_active=date
#                     )
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)
#         return user
#
#     @class_connection
#     async def add_new_user(self, session: AsyncSession, user_id: int, username: Optional[str], date: datetime):
#         user = await self.get_user_by_id(session, user_id)
#         if user is None:
#             user = await self.add_user(session, user_id, username, date)
#         else:
#             user.date_active = date
#             await session.commit()
#
#
# class BlockedUser:
#
#     @class_connection
#     async def get_blocked_value(self, session: AsyncSession, user_id: int) -> bool:
#         return await session.get(User.blocked, user_id)

class UserRegistration:
    def __init__(self):
        self.session = async_session

    @staticmethod
    async def _new_user(session: AsyncSession, message: Message):
        date = datetime.now()
        referral_id = int(message.text.split()[1]) if "/start " in message.text else None
        user = User(user_id=message.from_user.id,
                    username=message.from_user.username,
                    date_registration=date,
                    referral_id=referral_id,
                    date_active=date)
        session.add(user)
        await session.commit()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        return await session.get(User, user_id)

    async def update_date_active(self, session: AsyncSession, user_id: int) -> None:
        date = datetime.now()
        user = await self.get_user_by_id(session, user_id)
        user.date_active = date
        await session.commit()

    async def create_user(self, message: Message):
        async with self.session() as session:
            user = await self.get_user_by_id(session, message.from_user.id)
            if user is not None:
                await self.update_date_active(session, user.user_id)
            else:
                await self._new_user(session, message)
