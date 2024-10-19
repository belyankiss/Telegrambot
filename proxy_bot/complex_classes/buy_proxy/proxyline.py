from datetime import datetime, timedelta

import aiohttp

from proxy_bot.complex_classes.buy_proxy.exceptions import NoPlanError, NoMoneySiteError, UserNotMoneyProxyLineError
from proxy_bot.complex_classes.payments.payments_classes import CryptoBotPay
from proxy_bot.constants.msg_constants import MessageToAdminAfterBuy, ShortButton
from proxy_bot.db.models import Purchase
from proxy_bot.settings import settings


# order = {
#     'type': 'shared',  # dedicated or shared (если IPv6, тогда только dedicated)
#     'ip_version': 6,  # версия IP: 4 или 6
#     'country': 'us',  # код страны
#     'period': 360,  # 5, 10, 20, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360
#     'quantity': 1  # количество
# }
#
#
# async def get_countries():
#     countries = await open_url(Urls.COUNTRY)
#     for country in countries:
#         if country['code'] not in Constant.COUNTRIES_CODES:
#             Constant.COUNTRIES_CODES.append(country['code'])
#
#
# async def open_url(url: str) -> dict:
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url.format(API_KEY=API_KEY)) as response:
#             return await response.json()
#
#
# async def get_price(data: dict):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url=Urls.PRICE_PREVIEW.format(API_KEY=API_KEY), data=data) as response:
#             return await response.json()
#
#
# async def create_order(data: dict):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url=Urls.CREATE_ORDER.format(API_KEY=API_KEY), data=data) as response:
#             return await response.json()
#
#
#
# class Urls:
#     COUNTRY = 'https://panel.proxyline.net/api/countries/?api_key={API_KEY}'
#     BALANCE = 'https://panel.proxyline.net/api/balance/?api_key={API_KEY}'
#     PRICE_PREVIEW = 'https://panel.proxyline.net/api/new-order-amount/?api_key={API_KEY}'
#     CREATE_ORDER = 'https://panel.proxyline.net/api/new-order/?api_key={API_KEY}'
#
#
# class ProxyLineOrder:
#     API_KEY = settings.API_KEY_PROXY_LINE
#     BASE_URL = 'https://panel.proxyline.net/api/'
#     PRICE_URL = BASE_URL + f'new-order-amount/?api_key={API_KEY}'
#     BALANCE_URL = BASE_URL + f'balance/?api_key={API_KEY}'
#
#     def __init__(self, user_id: int):
#         self.user_id = user_id
#         self.user_orm = UserORM(user_id=user_id)
#         self.o_user = None
#
#         self.ip_version = None
#         self.type = 'dedicated'
#         self.country: Optional[str] = None
#         self.period = None
#         self.quantity = 1
#
#         self.percentage = settings.PERCENTAGE
#         self.price_usdt = 0
#         self.price_rub = 0
#         self.balance_site = 0
#         self.order_text = ''
#         self.data = {}
#         self.ip_list = []
#
#     async def get_user_data(self):
#         async with self.user_orm.session() as session:
#             self.o_user = await self.user_orm.is_exist_user(session)
#
#     @staticmethod
#     async def get_site_balance():
#         response = await open_url(Urls.BALANCE)
#         return response.get('balance')
#
#     async def get_price_preview(self):
#         await self.get_user_data()
#         await self.get_site_balance()
#         self.data = {
#             'type': self.type,
#             'ip_version': self.ip_version,
#             'country': self.country,
#             'period': self.period,
#             'quantity': self.quantity
#         }
#         response = await get_price(self.data)
#         if response.get('non_field_errors') is not None:
#             raise NoPlanError()
#         self.price_usdt = response['amount']
#         balance_site = await self.get_site_balance()
#         if self.price_usdt > balance_site:
#             raise NoMoneySiteError(round(await CryptoBotPay.exchange(balance_site), 2))
#         self.price_rub = await CryptoBotPay.exchange(self.price_usdt)
#         price_including_interest = self.price_rub * settings.PERCENTAGE
#         if price_including_interest > self.o_user.balance:
#             raise UserNotMoneyProxyLineError(amount=price_including_interest)
#         return round(price_including_interest, 2)
#
#     async def buy_proxy(self):
#         response = await create_order(self.data)
#         try:
#             self.ip_list: List = response['data']['ip_list']
#             proxy_list = await self.user_orm.minus_balance(price=self.price_rub)
#                 # user_id=self.user_id,
#                 # amount=self.price_rub,
#                 # ip_version=self.ip_version,
#                 # period=self.period,
#                 # proxies=self.ip_list)
#             return proxy_list
#
#         except KeyError:
#             return []
#
#     async def buy_with_discount(self):
#         self.price_rub = self.price_rub * (1 - self.o_user.discount)
#         return await self.buy_proxy()
#
#         #{'amount': 0.96, 'data': {'ip_list': [], 'period': 5, 'country': 'gr', 'type': 'dedicated', 'ip_version': 4, 'quantity': 1}}
#
#
# if __name__ == '__main__':
#     p = ProxyLineOrder(1)
#     print(asyncio.run(p.get_site_balance()))

class CreateOrder:
    def __init__(self):
        self.type: str = 'dedicated'
        self.ip_version: int = 0
        self.country: str = ''
        self.period: int = 0
        self.quantity: int = 1


class ProxyLineAPI:
    API_KEY = settings.API_KEY_PROXY_LINE

    def __init__(self, order: CreateOrder = None):
        self._data = order.__dict__ if order is not None else None
        self.preview_price_link = f'https://panel.proxyline.net/api/new-order-amount/?api_key={self.API_KEY}'
        self.create_order_link = f'https://panel.proxyline.net/api/new-order/?api_key={self.API_KEY}'
        self.get_balance_link = f'https://panel.proxyline.net/api/balance/?api_key={self.API_KEY}'

    async def get_site_balance(self):
        usdt = (await self._get(self.get_balance_link)).get("balance")
        return round(await CryptoBotPay.exchange(usdt), 2)

    async def get_preview_price(self):
        response = await self._post(self.preview_price_link)
        if response.get("non_field_errors") is not None:
            raise NoPlanError()
        price_proxy = response.get("amount", None)
        return round(await CryptoBotPay.exchange(price_proxy), 2)

    async def create_order(self):
        response = await self._post(self.create_order_link)
        if response.get("non_field_errors") is not None:
            raise NoMoneySiteError(balance=await self.get_site_balance())
        return response

    async def _post(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=self._data) as response:
                return await response.json()

    @staticmethod
    async def _get(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                return await response.json()


class CreatePurchase:
    def __init__(self,
                 user_id: int,
                 order: CreateOrder = None,
                 ):
        from proxy_bot.db.requests_db import UserORM, PurchaseORM
        self.api = ProxyLineAPI(order)
        self.order = order
        self.user_id = user_id
        self.username = None
        self.user_discount = None
        self.user_orm = UserORM(user_id=user_id)
        self.purchase_orm = PurchaseORM(user_id=user_id)
        self.price_with_comision = None
        self.proxies = []
        self.message = ""

        self._user_balance = None
        self._site_balance = None
        self._clean_price = None

    async def _get_preview_price_comision(self):
        self._clean_price = await self.api.get_preview_price()
        self.price_with_comision = round(self._clean_price * settings.PERCENTAGE, 2)

    async def _get_user_balance(self):
        async with self.user_orm.session() as session:
            user = await self.user_orm.is_exist_user(session)
            self._user_balance = user.balance
            self.username = user.username
            self.user_discount = user.discount

    async def _check_user_balance(self):
        if self._user_balance < self.price_with_comision:
            raise UserNotMoneyProxyLineError(amount=round(self.price_with_comision - self._user_balance, 2))

    async def _check_balance_site(self):
        await self._get_preview_price_comision()
        self._site_balance = await self.api.get_site_balance()
        if self._site_balance < self._clean_price:
            raise NoMoneySiteError(balance=self._site_balance)

    async def show_preview(self):
        await self._check_balance_site()
        await self._get_user_balance()
        await self._check_user_balance()

    async def _save_proxies_in_DB(self, proxies: list):
        amount = round(self.price_with_comision / len(proxies), 2)
        for proxy in proxies:
            if self.order.ip_version == 4:
                host = proxy['ip']
            else:
                host = proxy['internal_ip']
            data_proxy = Purchase(user_id=self.user_id,
                                  host=host,
                                  port=proxy['port_http'],
                                  port_socks=proxy['port_socks5'],
                                  password=proxy['password'],
                                  username=proxy['username'],
                                  country=proxy['country'],
                                  city=None,
                                  purchase_time=datetime.now(),
                                  end_time=datetime.now() + timedelta(int(self.order.period)),
                                  amount=amount,
                                  product_type='scrolling')
            await self._create_message_to_user(data_proxy)
            await self.purchase_orm.save_proxyline_purchase(data_proxy)

    async def _change_user_balance(self):
        await self.user_orm.minus_balance(price=self.price_with_comision)

    async def _create_message_to_admin(self) -> str:
        return MessageToAdminAfterBuy(username=self.username,
                                      category=ShortButton.scrolling,
                                      count=self.order.quantity,
                                      price=self.price_with_comision).text

    async def _create_message_to_user(self, proxy: Purchase):
        self.message += (f"HTTP:<code>{proxy.host}:{proxy.port}:{proxy.username}:{proxy.password}</code>\n"
                         f"SOCKS5:<code>{proxy.host}:{proxy.port_socks}:{proxy.username}:{proxy.password}</code>")

    async def create_order(self) -> str:
        response = await self.api.create_order()
        proxies: list = response['data']['ip_list']
        await self._save_proxies_in_DB(proxies)
        await self._change_user_balance()
        return await self._create_message_to_admin()
