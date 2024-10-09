from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from proxy_bot.cache_class.cache import Cache
from proxy_bot.cache_class.wrapper_to_user import user_information

start_router = Router()


@start_router.message(CommandStart())
@user_information
async def push_start(msg: Message):
    button = InlineKeyboardButton(text='Push me', callback_data='push')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await msg.answer('Hello my dear friend!!!', reply_markup=kb)
    print(Cache().CACHE)


@start_router.callback_query(F.data == 'push')
@user_information
async def check(call: CallbackQuery):
    await call.message.edit_text('All fine!')
    print(Cache().CACHE)
