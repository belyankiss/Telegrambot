from typing import Union

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.msg_constants import MainProfile, UserPurchasesPage, ForSinglePurchase, ChoosePayment, \
    WriteToAdministration
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.db.requests_db import UserProfile
from proxy_bot.imports import bot
from proxy_bot.settings import settings

profile_router = Router()


class MessageToAdmin(StatesGroup):
    message = State()


@profile_router.message(F.text == '👨🏼‍💻 Профиль')
@profile_router.callback_query(F.data == 'profile')
@user_information
async def profile_1(event: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    user_profile = UserProfile(event.from_user.id)
    data_for_profile = await user_profile.get_info_user_for_profile()
    profile_user = MainProfile(data_for_profile)
    await SendUser(profile_user.text, profile_user.buttons)(event)


@profile_router.callback_query(F.data == 'purchases')
async def profile_2(call: CallbackQuery):
    user_profile = UserProfile(call.from_user.id)
    list_purchases = await user_profile.get_user_purchases()
    all_purchases = UserPurchasesPage(list_purchases)
    await SendUser(all_purchases.text, all_purchases.buttons, all_purchases.size)(call)


@profile_router.callback_query(F.data.startswith('purchase_user'))
async def profile_3(call: CallbackQuery):
    user_profile = UserProfile(call.from_user.id)
    data_purchase = await user_profile.get_one_purchase(int(call.data.split(':')[1]))
    single_purchase = ForSinglePurchase(data_purchase)
    await SendUser(single_purchase.text, single_purchase.buttons)(call)


@profile_router.callback_query(F.data == 'payment')
async def profile_3(call: CallbackQuery):
    await SendUser(**ChoosePayment().__dict__)(call)


@profile_router.callback_query(F.data == 'msg_admin')
async def profile_4(call: CallbackQuery, state: FSMContext):
    await state.set_state(MessageToAdmin.message)
    await state.update_data(id=settings.ADMIN)
    await SendUser(WriteToAdministration.to_admin, WriteToAdministration.back_profile)(call)


@profile_router.callback_query(F.data == 'advertising')
async def profile_5(call: CallbackQuery, state: FSMContext):
    await state.set_state(MessageToAdmin.message)
    await state.update_data(id=settings.ABOUT_ADV)
    await SendUser(WriteToAdministration.about_adv, WriteToAdministration.back_profile)(call)


@profile_router.message(MessageToAdmin.message)
async def profile_4_1(msg: Message, state: FSMContext):
    data = await state.get_data()
    whose = data.get('id')
    await bot.forward_message(chat_id=whose,
                              message_id=msg.message_id,
                              from_chat_id=msg.from_user.id)
    await state.clear()
    await SendUser(WriteToAdministration.message_send, WriteToAdministration.back_profile)(msg)
