#  async cache
""" Use this package for save any vars in cache"""

from asyncio import Lock
from typing import Any, Optional


class CacheUser:
    _instance = None
    CACHE = {}
    lock = Lock()
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CacheUser, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def add(cls, key: Any, value: Any) -> None:
        """
        Add in cache new_item
        :param key: Any immutable
        :param value: Any
        :return: None
        """
        async with cls.lock:
            cls.CACHE[key] = value

    @classmethod
    async def get(cls, key: Any) -> Optional[Any]:
        async with cls.lock:
            return cls.CACHE.get(key, False)

    @classmethod
    async def delete(cls, key: Any) -> None:
        async with cls.lock:
            cls.CACHE.pop(key, None)