from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from proxy_bot.complex_classes.discounts.discount_class import ActivateDiscount
from proxy_bot.complex_classes.discounts.exceptions import (NotDiscountTextError,
                                                            DiscountNotInBaseError,
                                                            UserHaveDiscountError,
                                                            DiscountWasActivatedError,
                                                            NotActivatesError)
from proxy_bot.constants.msg_constants import GetDiscountNameMessage, DiscountActivateSuccess, MenuButton
from proxy_bot.custom_sender.send_class import SendUser

discount_router = Router()


class Discount(StatesGroup):
    discount = State()


@discount_router.message(F.text == MenuButton.DISCOUNT)
async def discount_1(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Discount.discount)
    await SendUser(GetDiscountNameMessage())(msg)


@discount_router.message(Discount.discount)
async def discount_2(msg: Message, state: FSMContext):
    await state.clear()
    try:
        discount = ActivateDiscount(msg)
        percentage = await discount.activate()
        text = DiscountActivateSuccess(percentage=percentage).text
    except (NotDiscountTextError,
            DiscountNotInBaseError,
            UserHaveDiscountError,
            DiscountWasActivatedError,
            NotActivatesError) as e:
        text = e.text
    await SendUser(text=text)(msg)
