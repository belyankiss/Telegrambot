from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.msg_constants import Start, UserNotMember, UserNotSubscribe
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.helpers import check_member_user

start_router = Router()


@start_router.message(CommandStart(), F.chat.type == 'private')
@user_information
async def send_start(msg: Message):
    logger.debug("Start button pressed")
    if await check_member_user(msg.from_user.id):
        text = Start.text.format(username=msg.from_user.username)
        buttons = Start.buttons
        size = 2
    else:
        text = UserNotMember.text
        buttons = UserNotMember.buttons
        size = 1
    await SendUser(text, buttons, size=size)(msg)


@start_router.callback_query(F.data == 'check_subscribe')
@user_information
async def checking_subscribed(call: CallbackQuery):
    if await check_member_user(call.from_user.id):
        text = Start.text.format(username=call.from_user.username)
        buttons = Start.buttons
        size = 2
        await SendUser(text, buttons, size=size, delete=True)(call.message)
    else:
        text = UserNotSubscribe.text
        buttons = UserNotSubscribe.buttons
        size = 1
        await SendUser(text, buttons, size=size, delete=True)(call)
