from typing import Union

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.constants.load_constants import Constant
from proxy_bot.constants.msg_constants import MenuButton, MainProxyPage, ChooseWorkProxy, NotProxyMessage
from proxy_bot.custom_sender.send_class import SendUser, SendAdmins
from proxy_bot.imports import bot

proxy_router = Router()


@proxy_router.message(F.text == MenuButton.PROXIES, F.chat.type == 'private')
@proxy_router.callback_query(F.data == 'shop')
@user_information
async def proxy_page_1(event: Union[Message, CallbackQuery]):
    await SendUser(MainProxyPage())(event)


@proxy_router.callback_query(F.data == 'working')
async def proxy_page_2(call: CallbackQuery):
    if len(Constant.PROXIES_WORK) == 0:
        await bot.answer_callback_query(callback_query_id=call.id, text=NotProxyMessage.text, show_alert=True)
        if not Constant.NO_PROXY:
            await SendAdmins().to_all_admins(NotProxyMessage.text_for_admin)
            Constant.NO_PROXY = True
    else:
        await SendUser(ChooseWorkProxy())(call)
