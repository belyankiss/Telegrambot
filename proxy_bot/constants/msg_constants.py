from datetime import datetime

from proxy_bot.settings import settings


class CreatorMessages:
    text: str = ''
    buttons = [] or {}
    size: int = 1


#  messages for start page

class Start(CreatorMessages):
    text = ("👋 Привет, {username}\n\n"
            "<u>❗Обязательно ознакомься с правилами нашего магазина, можешь прочитать</u> "
            f"<a href='{settings.URL_RULES}'>👉 "
            "ТУТ</a>")
    buttons = ['👨🏼‍💻 Профиль', '🔐 Аренда прокси',
               '🔤 Уникализатор', '🧑‍💻 Промокоды']


class UserNotMember(CreatorMessages):
    text = "👁 Для пользования ботом, тебе необходимо подписаться на канал ниже! 👇"
    buttons = {f'Подписаться {settings.CHAT_NAME}': settings.CHAT_SUB_LINK,
               '✅ Подписался': 'check_subscribe'}


class UserNotSubscribe(UserNotMember):
    text = "❌ Вы меня не обманете! Тебе необходимо подписаться на канал ниже для пользования ботом! 👇"


class IfUserBlocked(CreatorMessages):
    text = "❌ Администрация заблокировала вас в боте!"


class ForAdminAfterRegistration(CreatorMessages):
    text = ("❗️Пользователь @{username}\n\n"
            "Только что зарегистрировался в боте!\n"
            f"{datetime.now().strftime('%d-%m-%Y %H:%M')}")


# _______________________________________________________________________________________________________________________


if __name__ == '__main__':
    print(IfUserBlocked.__dict__)
