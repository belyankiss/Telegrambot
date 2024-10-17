import asyncio
from typing import Optional, Union

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from loguru import logger

from proxy_bot.constants.load_constants import Constant
from proxy_bot.constants.msg_constants import CreatorMessages
from proxy_bot.custom_sender.creator_keyboard import Keyboard
from proxy_bot.imports import bot


class SendUser:
    def __init__(self,
                 message: Optional[CreatorMessages] = None,
                 text: Optional[str] = None,
                 buttons: Optional[Union[dict, list]] = None,
                 photo: Union[str, bool] = False,
                 size: int = 1,
                 ):
        create_markup = Keyboard()
        if message is not None:
            self.photo = message.photo
            self.text = message.text
            self.reply_markup = create_markup(message.buttons, message.size)
        else:
            self.text = text
            self.reply_markup = create_markup(buttons, size)
            self.photo: Union[str, bool] = photo

    async def _answer_without_photo(self, message: Message):
        await message.answer(text=self.text, reply_markup=self.reply_markup)

    async def _answer_with_photo(self, message: Message):
        await message.answer_photo(caption=self.text, reply_markup=self.reply_markup, photo=self.photo)

    async def _edit_text(self, callback: CallbackQuery):
        await callback.message.edit_text(text=self.text, reply_markup=self.reply_markup)

    async def _edit_caption(self, callback: CallbackQuery):
        await callback.message.edit_caption(caption=self.text, reply_markup=self.reply_markup)

    async def __call__(self, event: Union[Message, CallbackQuery]):
        if isinstance(event, Message):
            try:
                await event.delete()
            except TelegramBadRequest:
                pass
            if self.photo:
                await self._answer_with_photo(event)
            else:
                await self._answer_without_photo(event)
        else:
            if event.message.caption is not None:
                await self._edit_caption(event)
            else:
                await self._edit_text(event)



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
