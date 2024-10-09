import functools
from typing import Union

from aiogram.types import CallbackQuery, Message

from proxy_bot.complex_classes.check_cache import CacheUser
from proxy_bot.db.models import User


def user_information(function):
    @functools.wraps(function)
    async def wrapper(event: Union[Message, CallbackQuery], *args, **kwargs):
        from_cache = CacheUser()
        user: User = await from_cache.get_user(event)
        if not user.blocked:
            return await function(event, *args, **kwargs)
        else:
            message = event if isinstance(event, Message) else event.message
            await message.answer(text="Вы заблокированы!")

    return wrapper
