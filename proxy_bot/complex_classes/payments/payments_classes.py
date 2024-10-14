import asyncio
import random
from abc import ABC, abstractmethod
from typing import List

import xrocket
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import PaidButtons, CurrencyType
from aiocryptopay.models.invoice import Invoice
from aiocryptopay.models.rates import ExchangeRate
from aiogram.types import Message
from aioyoomoney import Quickpay, Client
from aioyoomoney.enums.quickpay import PaymentType

from proxy_bot.complex_classes.payments.exceptions import UnderZeroError, WrongAmountError, XRocketException
from proxy_bot.settings import settings

CRYPTOBOT = AioCryptoPay(token=settings.CRYPTOBOT_TOKEN, network=Networks.MAIN_NET)
XROCKET = xrocket.PayAPI(settings.XROCKET_TOKEN)
YOOMONEY = Client(settings.YOOMONEY_TOKEN)


class PayBase(ABC):
    def __init__(self, amount: float):
        self.amount = amount
        self.invoice_id = None

    @staticmethod
    def create_id_check():
        id_check = random.randint(10000, 9999999)
        return id_check

    @abstractmethod
    async def create_invoice(self):
        pass

    @abstractmethod
    async def get_invoice_url(self):
        pass

    @abstractmethod
    async def check_payment(self) -> bool:
        pass


class CryptoBotPay(PayBase):
    accepted_assets = ['USDT', 'USDC', 'BTC', 'ETH', 'LTC', 'TRX', 'TON', ]

    def __init__(self, amount: float):
        super().__init__(amount=amount)

    async def create_invoice(self) -> Invoice:
        return await CRYPTOBOT.create_invoice(fiat='RUB',
                                              currency_type=CurrencyType.FIAT,
                                              amount=self.amount,
                                              description=f'#{self.create_id_check()}',
                                              paid_btn_name=PaidButtons.OPEN_BOT,
                                              paid_btn_url=settings.HREF_REF,
                                              accepted_assets=self.accepted_assets)

    async def get_invoice_url(self) -> str:
        invoice = await self.create_invoice()
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


class YooMoneyPay(PayBase):

    def __init__(self, amount: float):
        super().__init__(amount=amount)

    async def create_invoice(self):
        self.invoice_id = self.create_id_check()
        quick_pay = Quickpay(
            receiver=settings.RECEIVER_YOOMONEY,
            sum=self.amount,
            payment_type=PaymentType.AC,
            label=f'{self.invoice_id}'
        )
        async with quick_pay as pay:
            return str(pay.url)

    async def get_invoice_url(self):
        return await self.create_invoice()

    async def check_payment(self):
        count = 120
        while True:
            history = await YOOMONEY.operation_history()
            labels = [operation.label for operation in history.operations]
            if str(self.invoice_id) in labels:
                return True
            else:
                await asyncio.sleep(5)
                if count < 0:
                    return False
            count -= 1


class XRocketPay(PayBase, ABC):
    accepted_assets = ["TONCOIN", "BTC", "USDT", "TRX", "ETH", "BNB"]

    def __init__(self, amount: float, currency: str):
        self.currency = currency
        self.amount_for_balance = None
        super().__init__(amount=amount)

    async def create_invoice(self):
        await self.exchange()
        return await XROCKET.invoice_create(currency=self.currency,
                                            amount=self.amount)

    async def get_invoice_url(self):
        data: dict = await self.create_invoice()
        if not data.get('success'):
            raise XRocketException()
        self.invoice_id = data['data']['id']
        return data['data']['link']

    async def check_payment(self):
        count = 120
        while True:
            history = await XROCKET.invoice_info(self.invoice_id)
            if history.get('success'):
                if history['data']['paid'] is not None:
                    await XROCKET.invoice_delete(self.invoice_id)
                    return True
                else:
                    await asyncio.sleep(5)
                    if count < 0:
                        return False
                count -= 1
            else:
                break

    async def exchange(self):
        ex: List[ExchangeRate] = await CRYPTOBOT.get_exchange_rates()
        if self.currency == "TONCOIN":
            self.currency = "TON"
        for item in ex:
            if item.source == self.currency and item.target == "RUB":
                self.amount_for_balance = self.amount * item.rate


class Pay:
    def __init__(self, msg: Message, payment: str, currency: str = None):
        self.msg = msg
        self.amount = self._is_right_amount(msg)
        if payment == 'cryptobot':
            self.payment = CryptoBotPay(self.amount)
        elif payment == 'yoomoney':
            self.payment = YooMoneyPay(self.amount)
        else:
            self.payment = XRocketPay(self.amount, currency)

    @staticmethod
    def _is_right_amount(msg):
        try:
            amount = float(msg.text)
            if amount <= 0:
                raise UnderZeroError()
            return amount
        except ValueError:
            raise WrongAmountError()


if __name__ == '__main__':
    x = XRocketPay(1, '')
    print(asyncio.run(x.exchange()))
