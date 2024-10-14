from typing import Optional, Union

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class Keyboard:

    @staticmethod
    def _reply_markup(buttons: Optional[list] = None, size: int = 1) -> Optional[ReplyKeyboardMarkup]:
        if buttons is not None:
            keyboard = ReplyKeyboardBuilder()
            keyboard.add(*[KeyboardButton(text=text) for text in buttons])
            return keyboard.adjust(size).as_markup(resize_keyboard=True)

    @staticmethod
    def _inline_markup(buttons: Optional[dict] = None, size: int = 1) -> Optional[InlineKeyboardMarkup]:
        if buttons is not None:
            keyboard = InlineKeyboardBuilder()
            for text, callback in buttons.items():
                if 'https' in callback:
                    keyboard.add(InlineKeyboardButton(text=text, url=f'{callback}'))
                else:
                    keyboard.add(InlineKeyboardButton(text=text, callback_data=callback))
            return keyboard.adjust(size).as_markup()

    def __call__(self, buttons: Optional[Union[list, dict]] = None, size: int = 1) -> \
            Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]]:

        if isinstance(buttons, list):
            return self._reply_markup(buttons, size)
        else:
            return self._inline_markup(buttons, size)


if __name__ == '__main__':
    m_buttons = {'Hello': 'hello', 'Hi': 'hi', 'True': 'true'}
    kb = Keyboard()
    print(kb(m_buttons))
