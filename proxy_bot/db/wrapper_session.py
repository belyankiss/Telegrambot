import functools

from proxy_bot.db.create_async_session import async_session


def class_connection(func):
    """
    This wrapper for class methods
    :param func:
    :return:
    """
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with async_session() as session:
            return await func(self, session, *args, **kwargs)
    return wrapper

def def_connection(func):
    """
    This wrapper for def methods
    :param func:
    :return:
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper