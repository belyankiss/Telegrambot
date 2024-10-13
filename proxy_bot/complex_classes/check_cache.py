from typing import Union

from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.cache import Cache
from proxy_bot.db.requests_db import UserRegistration


class CacheUser(Cache, UserRegistration):
    async def get_user(self, event: Union[Message, CallbackQuery]):
        user_id = event.from_user.id
        async with self.session() as session:
            user = await self.get(user_id)  # search in cache
            if user:
                await self.update_date_active(session, user_id, event.from_user.username)
                return user
            user = await self.get_user_by_id(session, user_id)  # search in database
            if user is not None:
                await self.add(user_id, user)  # add to cache
                await self.update_date_active(session, user_id, event.from_user.username)  # save changes in database
                return user
            user = await self.new_user(session, event)  # create a new user
            await self.add(user_id, user)  # add new user in cache
            return user
