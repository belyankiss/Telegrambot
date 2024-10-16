from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from proxy_bot.complex_classes.payments.exceptions import UnderZeroError, WrongAmountError, XRocketException
from proxy_bot.complex_classes.payments.payments_classes import Pay
from proxy_bot.constants.msg_constants import ChoicePayment, ForXrocket, PaymentMessage, UpBalance, NoPayment
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.db.requests_db import UserORM

pay_router = Router()


class Amount(StatesGroup):
    amount = State()


@pay_router.callback_query(F.data == 'cryptobot')
async def pay_cryptobot(call: CallbackQuery, state: FSMContext):
    await state.set_state(Amount.amount)
    await state.update_data(payment=call.data)
    await SendUser(**ChoicePayment(payment=call.data)())(call)


@pay_router.callback_query(F.data == 'yoomoney')
async def pay_yoomoney(call: CallbackQuery, state: FSMContext):
    await state.set_state(Amount.amount)
    await state.update_data(payment=call.data)
    await SendUser(**ChoicePayment(payment=call.data)())(call)


@pay_router.callback_query(F.data == 'xrocket')
async def pay_xrocket(call: CallbackQuery, state: FSMContext):
    await state.update_data(payment=call.data)
    await SendUser(**ChoicePayment(payment=call.data)())(call)


@pay_router.callback_query(F.data.startswith("x_cur"))
async def pay_xrocket(call: CallbackQuery, state: FSMContext):
    currency = call.data.split(":")[1]
    await state.set_state(Amount.amount)
    await state.update_data(currency=currency)
    await SendUser(**ForXrocket(currency=currency)())(call)


@pay_router.message(Amount.amount)
async def get_amount(msg: Message, state: FSMContext):
    data = await state.get_data()
    payment = data.get("payment")
    currency = data.get("currency")
    try:
        paying = Pay(msg, payment, currency)
        invoice_url = await paying.payment.get_invoice_url()
        if currency is not None:
            amount: float = paying.payment.amount_for_balance
        else:
            amount = float(msg.text)
        await SendUser(**PaymentMessage(amount=msg.text, currency=currency, invoice_url=invoice_url)())(msg)
        if await paying.payment.check_payment():
            await SendUser(**UpBalance(amount=amount)())(msg)
            await UserORM(msg).update_balance(amount)
        else:
            await SendUser(**NoPayment()())(msg)
        await state.clear()

    except (UnderZeroError, WrongAmountError, XRocketException) as e:
        await SendUser(text=e.text)(msg)
        if isinstance(e, XRocketException):
            await state.clear()
