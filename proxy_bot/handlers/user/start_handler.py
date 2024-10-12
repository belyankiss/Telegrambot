from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.load_constants import Constant
from proxy_bot.constants.msg_constants import Start, UserNotMember, UserNotSubscribe, AdminPanel
from proxy_bot.custom_sender.send_class import SendUser
from proxy_bot.helpers import check_member_user

start_router = Router()


@start_router.message(CommandStart(), F.chat.type == 'private')
@user_information
async def send_start(msg: Message):
    if await check_member_user(msg.from_user.id):
        start = Start(username=msg.from_user.username)
        text = start.text
        buttons = start.buttons
        size = start.size
    else:
        not_member = UserNotMember()
        text = not_member.text
        buttons = not_member.buttons
        size = 1
    await SendUser(text, buttons, size=size)(msg)


@start_router.callback_query(F.data == 'check_subscribe')
@user_information
async def checking_subscribed(call: CallbackQuery):
    if await check_member_user(call.from_user.id):
        start = Start(username=call.from_user.username)
        text = start.text
        buttons = start.buttons
        size = start.size
        await SendUser(text, buttons, size=size, delete=True)(call.message)
    else:
        not_subscribe = UserNotSubscribe()
        text = not_subscribe.text
        buttons = not_subscribe.buttons
        size = 1
        await SendUser(text, buttons, size=size, delete=True)(call)


@start_router.message(F.text == '/admin', F.chat.type == "private", F.from_user.id.in_(Constant.ADMINS))
async def admin_panel(msg: Message):
    await SendUser(**AdminPanel().__dict__)(msg)
