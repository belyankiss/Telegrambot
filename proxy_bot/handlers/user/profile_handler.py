from typing import Union

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.msg_constants import MainProfile, UserPurchasesPage, ForSinglePurchase
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.db.requests_db import UserProfile

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
    await SendUser(MainProfile.create_text(data_for_profile), MainProfile.buttons)(event)
    await state.update_data(user_profile=user_profile)


@profile_router.callback_query(F.data == 'purchases')
async def profile_2(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_profile: UserProfile = data.get('user_profile')
    list_purchases = await user_profile.get_user_purchases()
    buttons, size = UserPurchasesPage.create_buttons(list_purchases)
    await SendUser(UserPurchasesPage.create_text(list_purchases), buttons=buttons, size=size)(call)


@profile_router.callback_query(F.data.startswith('purchase_user'))
async def profile_3(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_profile: UserProfile = data.get('user_profile')
    data_purchase = await user_profile.get_one_purchase(int(call.data.split(':')[1]))
    await SendUser(ForSinglePurchase.create_text(data_purchase), ForSinglePurchase.buttons)(call)
