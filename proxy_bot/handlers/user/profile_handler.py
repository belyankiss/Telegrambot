from typing import Union

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.msg_constants import MainProfile, UserPurchasesPage, ForSinglePurchase, ChoosePayment, \
    WriteToAdministration, MenuButton
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.db.requests_db import UserORM
from proxy_bot.imports import bot
from proxy_bot.settings import settings

profile_router = Router()


class MessageToAdmin(StatesGroup):
    message = State()


@profile_router.message(F.text == MenuButton.PROFILE)
@profile_router.callback_query(F.data == 'profile')
@user_information
async def profile_1(event: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    data_for_profile = await UserORM(event).user_profile_info()
    await SendUser(MainProfile(user_data=data_for_profile))(event)


@profile_router.callback_query(F.data == 'purchases')
async def profile_2(call: CallbackQuery):
    list_purchases = await UserORM(call).get_user_purchases()
    await SendUser(UserPurchasesPage(list_purchases=list_purchases))(call)


@profile_router.callback_query(F.data.startswith('purchase_user'))
async def profile_3(call: CallbackQuery):
    data_purchase = await UserORM(call).get_one_purchase(int(call.data.split(':')[1]))
    await SendUser(ForSinglePurchase(data_purchase=data_purchase))(call)


@profile_router.callback_query(F.data == 'payment')
async def profile_3(call: CallbackQuery):
    await SendUser(ChoosePayment())(call)


@profile_router.callback_query(F.data == 'msg_admin')
async def profile_4(call: CallbackQuery, state: FSMContext):
    await state.set_state(MessageToAdmin.message)
    await state.update_data(id=settings.ADMIN)
    await SendUser(text=WriteToAdministration.to_admin, buttons=WriteToAdministration.back_profile)(call)


@profile_router.callback_query(F.data == 'advertising')
async def profile_5(call: CallbackQuery, state: FSMContext):
    await state.set_state(MessageToAdmin.message)
    await state.update_data(id=settings.ABOUT_ADV)
    await SendUser(text=WriteToAdministration.about_adv, buttons=WriteToAdministration.back_profile)(call)


@profile_router.message(MessageToAdmin.message)
async def profile_4_1(msg: Message, state: FSMContext):
    data = await state.get_data()
    whose = data.get('id')
    await bot.forward_message(chat_id=whose,
                              message_id=msg.message_id,
                              from_chat_id=msg.from_user.id)
    await state.clear()
    await SendUser(text=WriteToAdministration.message_send, buttons=WriteToAdministration.back_profile)(msg)
