import asyncio

from proxy_bot.imports import bot
from proxy_bot.settings import settings


async def check_member_user(user_id: int):
    status = await bot.get_chat_member(chat_id=settings.CHAT_SUB_ID, user_id=user_id)
    if status.status == 'left':
        return False
    return True


if __name__ == '__main__':
    asyncio.run(check_member_user(123))
