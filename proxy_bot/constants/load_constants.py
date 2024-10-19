import aiohttp
from sqlalchemy import select

from proxy_bot.db.create_async_session import async_session
from proxy_bot.db.models import ProxyWork, Admin, Photo, ProxySort
from proxy_bot.settings import settings


class Constant:

    ADMINS = [settings.ADMIN, settings.CODER]
    PROXIES_WORK = []
    PROXIES_SORT = {}
    COUNTRIES = None

    NO_PROXY_WORK = False
    NO_PROXY_SORT = False
    NO_PROXY_PROXYLINE = False

    PROXY_WORK_DEATH = False
    PROXY_SORT_DEATH = False

    COUNTRIES_CODES = []

    PHOTOS = {}

    @classmethod
    async def _load_admins(cls):
        async with async_session() as session:
            admins = await session.scalars(select(Admin.user_id))
        for admin in admins:
            cls.ADMINS.append(admin[0])

    @classmethod
    async def _load_proxies_work(cls):
        from proxy_bot.db.requests_db import Proxies
        work_proxy = await Proxies(ProxyWork.__name__).get_proxies()
        for proxy in work_proxy:
            cls.PROXIES_WORK.append(proxy)

    @classmethod
    async def _load_proxies_sort(cls):
        from proxy_bot.db.requests_db import Proxies
        sort_proxy = await Proxies(ProxySort.__name__).get_proxies()
        cls.COUNTRIES = sorted(set([item.country for item in sort_proxy]))
        for country in cls.COUNTRIES:
            cls.PROXIES_SORT[country] = []
        for proxy in sort_proxy:
            cls.PROXIES_SORT[proxy.country].append(proxy)

    @classmethod
    async def _load_photos(cls):
        async with async_session() as session:
            photos = list(await session.scalars(select(Photo)))
        for photo in photos:
            cls.PHOTOS[photo.category] = photo.href_photo

    @classmethod
    async def _load_countries_codes(cls):
        url = f'https://panel.proxyline.net/api/countries/?api_key={settings.API_KEY_PROXY_LINE}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                countries = await response.json()
        for country in countries:
            if country['code'] not in Constant.COUNTRIES_CODES:
                cls.COUNTRIES_CODES.append(country['code'])

    async def load_data(self):
        await self._load_admins()
        await self._load_proxies_work()
        await self._load_proxies_sort()
        await self._load_photos()
        await self._load_countries_codes()


if __name__ == '__main__':
    print(ProxyWork.__name__)
