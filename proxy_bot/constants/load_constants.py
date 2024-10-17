import asyncio

from proxy_bot.settings import settings


class Constant:

    ADMINS = [settings.ADMIN, settings.CODER]
    PROXIES_WORK = []
    PROXIES_SORT = {}

    NO_PROXY = False
    PHOTOS = {}

    @classmethod
    async def _load_admins(cls):
        from proxy_bot.db.requests_db import AdminsORM
        admins = await AdminsORM.get_admins()
        for admin in admins:
            cls.ADMINS.append(admin[0])

    @classmethod
    async def _load_proxies_work(cls):
        from proxy_bot.db.requests_db import ProxyWorkORM
        work_proxy = await ProxyWorkORM().get_proxies()
        for proxy in work_proxy:
            cls.PROXIES_WORK.append(proxy)

    @classmethod
    async def _load_photos(cls):
        from proxy_bot.db.requests_db import load_photos
        photos = await load_photos()
        for photo in photos:
            cls.PHOTOS[photo.category] = photo.href_photo

    async def load_data(self):
        await self._load_admins()
        await self._load_proxies_work()
        await self._load_photos()


if __name__ == '__main__':
    asyncio.run(Constant().load_data())
    print(Constant.ADMINS)
