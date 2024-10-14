import asyncio
from typing import Optional, Union

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from loguru import logger

from proxy_bot.constants.load_constants import Constant
from proxy_bot.custom_sender.creator_keyboard import Keyboard
from proxy_bot.imports import bot


class SendUser:
    def __init__(self, text: str, buttons: Optional[Union[dict, list]] = None, size: int = 1, delete: bool = False):
        self.text = text
        self.reply_markup = Keyboard()(buttons, size)
        self.delete = delete

    async def _if_callback(self, event):
        try:
            if not event.message.caption:
                await event.message.edit_text(text=self.text, reply_markup=self.reply_markup)
            else:
                await event.message.edit_caption(caption=self.text, reply_markup=self.reply_markup)
        except TelegramBadRequest:
            pass

    async def _if_message(self, event, photo):
        try:
            await event.delete()
        except TelegramBadRequest:
            pass
        if photo is None:
            await event.answer(text=self.text, reply_markup=self.reply_markup)
        else:
            await event.answer_photo(caption=self.text, photo=photo, reply_markup=self.reply_markup)

    async def __call__(self, event: Union[Message, CallbackQuery], photo: str = None):
        if isinstance(event, CallbackQuery):
            await self._if_callback(event)
        else:
            await self._if_message(event, photo)


class SendAdmins:
    def __init__(self):
        self.admins_list = Constant.ADMINS

    async def to_all_admins(self, text):
        for admin in self.admins_list:
            try:
                await bot.send_message(chat_id=admin, text=text)
                await asyncio.sleep(0.3)
            except (TelegramForbiddenError, TelegramBadRequest) as e:
                logger.warning(f"{e} {admin}")

    @staticmethod
    async def send_one_admin(text: str, admin_id: int, buttons: Optional[dict] = None):
        reply_markup = Keyboard()(buttons)
        try:
            await bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup)
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logger.warning(f"{e} {admin_id}")


if __name__ == '__main__':
    pass
