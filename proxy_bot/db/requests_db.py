from datetime import datetime
from typing import Optional, Union

from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from proxy_bot.constants.msg_constants import ForAdminAfterRegistration
from proxy_bot.custom_sender.send_class import SendAdmins
from proxy_bot.db.create_async_session import async_session
from proxy_bot.db.models import User


class UserRegistration:
    def __init__(self):
        self.session = async_session
        self.to_admin = SendAdmins()

    async def new_user(self, session: AsyncSession, event: Union[Message, CallbackQuery]):
        date = datetime.now()
        referral_id = int(event.text.split()[1]) if "/start " in event.text else None
        user = User(user_id=event.from_user.id,
                    username=event.from_user.username,
                    date_registration=date,
                    referral_id=referral_id,
                    date_active=date)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        text = ForAdminAfterRegistration.text.format(username=event.from_user.username)
        await self.to_admin.to_all_admins(text)  # send message to all admins after registration user
        return user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        return await session.get(User, user_id)


    async def update_date_active(self, session: AsyncSession, user_id: int) -> None:
        date = datetime.now()
        user = await self.get_user_by_id(session, user_id)
        user.date_active = date
        await session.commit()
        await session.refresh(user)
