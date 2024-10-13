import asyncio
import random

import xrocket
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import PaidButtons, CurrencyType
from aiocryptopay.models.invoice import Invoice
from aiogram.types import Message

from proxy_bot.complex_classes.payments.exceptions import UnderZeroError, WrongAmountError
from proxy_bot.settings import settings

CRYPTOBOT = AioCryptoPay(token=settings.CRYPTOBOT_TOKEN, network=Networks.MAIN_NET)
XROCKET = xrocket.PayAPI(settings.XROCKET_TOKEN)


class CryptoBotPay:
    accepted_assets = ['USDT', 'USDC', 'BTC', 'ETH', 'LTC', 'TRX', 'TON', ]

    def __init__(self, amount: float):
        self.amount = amount
        self.invoice_id = None

    @staticmethod
    def create_id_check():
        id_check = random.randint(10000, 9999999)
        return id_check

    async def _create_invoice(self) -> Invoice:
        return await CRYPTOBOT.create_invoice(fiat='RUB',
                                              currency_type=CurrencyType.FIAT,
                                              amount=self.amount,
                                              description=f'#{self.create_id_check()}',
                                              paid_btn_name=PaidButtons.OPEN_BOT,
                                              paid_btn_url=settings.HREF_REF,
                                              accepted_assets=self.accepted_assets)

    async def get_invoice_url(self) -> str:
        invoice = await self._create_invoice()
        self.invoice_id = invoice.invoice_id
        return invoice.bot_invoice_url

    async def check_payment(self) -> bool:
        count = 120
        while True:
            check_invoice = await CRYPTOBOT.get_invoices(invoice_ids=self.invoice_id)
            if check_invoice.status == 'paid':
                return True
            else:
                await asyncio.sleep(5)
                if count < 0:
                    return False
            count -= 1


class XRocketPay:
    pass


class YooMoneyPay:
    pass


class Pay:
    def __init__(self, msg: Message, payment: str):
        self.msg = msg
        self.amount = self.is_right_amount(msg)
        if payment == 'cryptobot':
            self.payment = CryptoBotPay(self.amount)
        elif payment == 'yoomoney':
            self.payment = YooMoneyPay()
        else:
            self.payment = XRocketPay()

    @staticmethod
    def is_right_amount(msg):
        try:
            amount = float(msg.text)
            if amount <= 0:
                raise UnderZeroError()
            return amount
        except ValueError:
            raise WrongAmountError()

# class CryptoBotPay:
#     accepted_assets = ['USDT', 'USDC', 'BTC', 'ETH', 'LTC', 'TRX', 'TON', ]
#
#     def __init__(
#             self,
#             msg: Message,
#             shop_asset: str = 'RUB',
#             back_url: Optional[str] = None
#     ):
#         """
#         Класс для оплаты через систему криптобот.
#         :param msg: Сообщение с суммой от пользователя.
#         :param shop_asset: Валюта магазина: RUB or USD
#         """
#         self.msg = msg
#         self.name = 'CryptoBot'
#         self.user_id = self.msg.from_user.id
#         self.amount = 0
#         self.invoice: Optional[Invoice] = None
#         self.invoice_id = None
#         self.shop_asset = shop_asset
#         self.back_url = back_url
#
#     @staticmethod
#     async def exchange(usdt: Optional[float] = None):
#         ex = await crypto.get_exchange_rates()
#         course = round(ex[0].rate, 2)
#         if usdt is not None:
#             return usdt * course * 0.97
#         return course * 0.97
#
#     @staticmethod
#     def create_id_check():
#         id_check = random.randint(10000, 9999999)
#         return id_check
#
#     async def _get_amount(self):
#         try:
#             amount = float(self.msg.text)
#             if amount <= 0:
#                 raise UnderZeroError()
#             else:
#                 self.amount = amount
#         except ValueError:
#             raise WrongAmountError()
#
#     async def _create_invoice(self):
#         self.invoice: Invoice = await crypto.create_invoice(fiat=self.shop_asset,
#                                                             currency_type=CurrencyType.FIAT,
#                                                             amount=self.amount,
#                                                             description=f'#{self.create_id_check()}',
#                                                             paid_btn_name=PaidButtons.OPEN_BOT,
#                                                             paid_btn_url=self.back_url,
#                                                             accepted_assets=self.accepted_assets)
#
#     async def _init_payment(self):
#         await self._get_amount()
#         await self._create_invoice()
#
#     async def get_url(self):
#         await self._init_payment()
#         self.invoice_id = self.invoice.invoice_id
#         return self.invoice.bot_invoice_url
#
#     async def check_payment_cryptobot(self) -> bool:
#         count = 120
#         while True:
#             check_invoice = await crypto.get_invoices(invoice_ids=self.invoice_id)
#             if check_invoice.status == 'paid':
#                 return True
#             else:
#                 await asyncio.sleep(5)
#                 if count < 0:
#                     return False
#             count -= 1
