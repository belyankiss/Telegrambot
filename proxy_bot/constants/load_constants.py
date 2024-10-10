import asyncio

from sqlalchemy import select

from proxy_bot.db.create_async_session import async_session
from proxy_bot.db.models import Admin
from proxy_bot.settings import settings


class Constant:
    ADMINS = [settings.ADMIN, settings.CODER]
    PROXIES_WORK = []
    PROXIES_SORT = {}

    @classmethod
    async def _load_admins(cls):
        async with async_session() as session:
            admins = await session.execute(select(Admin.user_id))
            for admin in admins:
                cls.ADMINS.append(admin[0])

    async def load_data(self):
        await self._load_admins()


if __name__ == '__main__':
    asyncio.run(Constant().load_data())
    print(Constant.ADMINS)
