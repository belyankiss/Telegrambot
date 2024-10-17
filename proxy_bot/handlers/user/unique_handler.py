from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.msg_constants import MainMessageUnique, GoodUniqueMessage, WrongUniqueMessage, MenuButton
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.helpers import Replacer

unique_router = Router()


class UniqueText(StatesGroup):
    text = State()


@unique_router.message(F.text == MenuButton.UNIQUE)
@user_information
async def unique_1(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(UniqueText.text)
    await SendUser(MainMessageUnique())(msg)


@unique_router.message(UniqueText.text)
async def unique_2(msg: Message, state: FSMContext):
    if msg.text and len(msg.text) > 0:
        unique_text = Replacer.replace_similar_letters_randomly(msg.text)
        text = GoodUniqueMessage(unique_text=unique_text)
        await state.update_data(text=msg.text)
    else:
        text = WrongUniqueMessage()
    await SendUser(**text())(msg)


@unique_router.callback_query(F.data == 'unique_again')
async def unique_3(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text_from_user = data.get('text')
    counter = data.get('counter')
    if counter is not None:
        counter += 1
    else:
        counter = 1
    unique_text = Replacer.replace_similar_letters_randomly(text_from_user)
    await state.update_data(counter=counter)
    await SendUser(GoodUniqueMessage(counter=counter, unique_text=unique_text))(call)
