import functools
from typing import Union

from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from proxy_bot.constants.msg_constants import IfUserBlocked
from proxy_bot.db.requests_db import UserORM


def user_information(function):
    @functools.wraps(function)
    async def wrapper(event: Union[Message, CallbackQuery], *args, **kwargs):
        user = UserORM(event)
        if not await user.is_blocked_user():
            return await function(event, *args, **kwargs)
        else:
            message = event if isinstance(event, Message) else event.message
            await message.answer(IfUserBlocked().text(), reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

    return wrapper
