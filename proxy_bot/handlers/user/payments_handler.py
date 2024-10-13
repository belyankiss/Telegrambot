from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from proxy_bot.constants.msg_constants import ChoicePayment
from proxy_bot.custom_sender.send_class import SendUser

pay_router = Router()


class Amount(StatesGroup):
    amount = State()


@pay_router.callback_query(F.data == 'cryptobot')
async def pay_cryptobot(call: CallbackQuery, state: FSMContext):
    await state.set_state(Amount.amount)
    await state.update_data(payment=call.data)
    await SendUser(ChoicePayment.cryptobot, ChoicePayment.back_keyboard)(call)


@pay_router.callback_query(F.data == 'yoomoney')
async def pay_cryptobot(call: CallbackQuery, state: FSMContext):
    await state.set_state(Amount.amount)
    await state.update_data(payment=call.data)
    await SendUser(ChoicePayment.yoomoney, ChoicePayment.back_keyboard)(call)


@pay_router.callback_query(F.data == 'xrocket')
async def pay_cryptobot(call: CallbackQuery, state: FSMContext):
    await state.set_state(Amount.amount)
    await state.update_data(payment=call.data)
    await SendUser(ChoicePayment.xrocket, ChoicePayment.back_keyboard)(call)


@pay_router.message(Amount.amount)
async def get_amount(msg: Message, state: FSMContext):
    ...
