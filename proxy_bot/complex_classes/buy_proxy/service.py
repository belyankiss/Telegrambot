from asyncio import Lock
from typing import Union

import aiohttp
from aiogram.types import BufferedInputFile
from aiohttp import ClientProxyConnectionError, ClientHttpProxyError

from proxy_bot.complex_classes.buy_proxy.exceptions import UserNotMoneyError, BadProxyError, ProxyDeathError, \
    NotEnoughProxyError, NotProxyInBaseError
from proxy_bot.constants.load_constants import Constant
from proxy_bot.constants.msg_constants import ProxyMessage, MessageToAdminAfterBuy, ShortButton
from proxy_bot.db.models import ProxySort, ProxyWork
from proxy_bot.db.requests_db import UserORM, PurchaseORM, Proxies
from proxy_bot.settings import settings

lock = Lock()


class SortedProxy:
    def __init__(self, count_proxy: int, country_code: str):
        self.count_proxy = count_proxy
        self.country_code = country_code
        self.price_proxy = settings.COUNTRY_PRICE_PROXY
        self.category = ShortButton.sort


class WorkedProxy:
    def __init__(self, count_proxy: int):
        self.count_proxy = count_proxy
        self.price_proxy = settings.PRICE_PROXY
        self.category = ShortButton.work


class CheckProxy:
    def __init__(self, count_proxy: int, proxy_list: list):
        self.count_proxy = count_proxy
        self.proxy_list = proxy_list
        self.user_proxy: list[Union[ProxyWork, ProxySort]] = []
        self.bad_proxy_sort: list[ProxySort] = []
        self.bad_proxy_work: list[ProxyWork] = []
        self.bad_proxy = []

        self._tablename = "ProxyWork" if self.proxy_list is Constant.PROXIES_WORK else "ProxySort"
        self._proxy_orm = Proxies(self._tablename)

    async def _get_proxy_to_user(self):
        async with lock:
            while len(self.user_proxy) < self.count_proxy:
                if len(self.proxy_list) > 0:
                    proxy: Union[ProxyWork, ProxySort] = self.proxy_list.pop(0)
                    await self._proxy_orm.update_busy_proxy(proxy.id)
                    self.user_proxy.append(proxy)
                else:
                    raise NotProxyInBaseError()

    @staticmethod
    async def check_proxy_aiohttp(proxy: Union[ProxyWork, ProxySort]):
        proxy_conf = f'http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}'
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url='https://example.com/', proxy=proxy_conf) as response:
                    if response.status != 200:
                        raise BadProxyError()
            except (ClientProxyConnectionError, ClientHttpProxyError):
                raise BadProxyError()

    async def _get_bad_proxy(self):
        self.bad_proxy_work, self.bad_proxy_sort = await self._proxy_orm.get_bad_proxy()
        self.bad_proxy = self.bad_proxy_sort if self._tablename == "ProxySort" else self.bad_proxy_work

    async def check_proxy(self) -> list[Union[ProxyWork, ProxySort]]:
        await self._get_bad_proxy()
        print(len(self.bad_proxy))
        await self._get_proxy_to_user()
        for proxy in self.user_proxy:
            try:
                await self.check_proxy_aiohttp(proxy)
            except BadProxyError:
                self.bad_proxy.append(proxy)
                proxy.work = False
                await self._proxy_orm.add_bad_proxy(proxy.id)
            if len(self.bad_proxy) > 10:
                await self._proxy_orm.kill_proxy()
                if self._tablename == "ProxyWork":
                    Constant.PROXIES_WORK = []
                else:
                    Constant.PROXIES_SORT = {}
                raise ProxyDeathError()
        self.user_proxy = [proxy for proxy in self.user_proxy if proxy.work == True]
        if self.user_proxy:
            return self.user_proxy
        else:
            await self.check_proxy()


class ProxyShop:
    def __init__(self,
                 proxy_data: Union[SortedProxy, WorkedProxy],
                 user_id: int,
                 ):
        self.proxy_data = proxy_data
        self.user_id = user_id

        self.user_orm = UserORM(user_id=user_id)
        self.purchase_orm = PurchaseORM(user_id=user_id)
        self.message = ""
        self.message_admin = ""
        self.file = None

    async def _check_balance_user(self):
        async with self.user_orm.session() as session:
            user = await self.user_orm.is_exist_user(session)
            if user.balance < self.proxy_data.price_proxy * self.proxy_data.count_proxy:
                raise UserNotMoneyError()

    async def _get_proxies(self):
        if isinstance(self.proxy_data, SortedProxy):
            self.proxies: list = Constant.PROXIES_SORT[self.proxy_data.country_code]
        else:
            self.proxies: list = Constant.PROXIES_WORK
        if len(self.proxies) < self.proxy_data.count_proxy:
            raise NotEnoughProxyError(len(self.proxies))
        if len(self.proxies) == 0:
            raise NotProxyInBaseError()

    async def _create_user_proxy_list(self):
        proxies = CheckProxy(self.proxy_data.count_proxy, self.proxies)
        self.user_proxy_list = await proxies.check_proxy()
        self.message = ProxyMessage(proxy_list=self.user_proxy_list).text

    async def _create_file(self):
        file = ''
        for proxy in self.user_proxy_list:
            file += f'{proxy.host}:{proxy.port}:{proxy.username}:{proxy.password}\n'
        file = file.encode("utf-8")
        if file:
            self.file = BufferedInputFile(file, filename="proxies.txt")

    async def _change_user_balance(self):
        price = len(self.user_proxy_list) * self.proxy_data.price_proxy
        user = await self.user_orm.minus_balance(price)
        self.message_admin = MessageToAdminAfterBuy(username=user.username,
                                                    category=self.proxy_data.category,
                                                    count=len(self.user_proxy_list),
                                                    price=price)

    async def _save_purchases(self):
        if self.user_proxy_list:
            for proxy in self.user_proxy_list:
                await self.purchase_orm.save_purchase(proxy, self.proxy_data.price_proxy)

    async def buy_proxy(self):
        await self._check_balance_user()
        await self._get_proxies()
        await self._create_user_proxy_list()
        await self._create_file()
        await self._change_user_balance()
        await self._save_purchases()
