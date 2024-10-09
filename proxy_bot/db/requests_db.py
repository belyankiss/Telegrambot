from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from proxy_bot.db.models import User
from proxy_bot.db.wrapper_session import class_connection


class NewUser:

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        return await session.get(User, user_id)

    @staticmethod
    async def add_user(session: AsyncSession, user_id: int, username: Optional[str], date: datetime) -> User:
        user = User(user_id=user_id,
                    username=username,
                    date_registration=date,
                    date_active=date
                    )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @class_connection
    async def add_new_user(self, session: AsyncSession, user_id: int, username: Optional[str], date: datetime):
        user = await self.get_user_by_id(session, user_id)
        if user is None:
            user = await self.add_user(session, user_id, username, date)
        else:
            user.date_active = date
            await session.commit()


class BlockedUser:

    @class_connection
    async def get_blocked_value(self, session: AsyncSession, user_id: int) -> bool:
        return await session.get(User.blocked, user_id)
