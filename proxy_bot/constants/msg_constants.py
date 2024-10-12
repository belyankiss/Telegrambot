from datetime import datetime
from typing import Optional, Union

from proxy_bot.settings import settings


class ShortButton:
    BACK = '🔙 Назад'
    work = '👨‍💻 Для ворка'
    scrolling = '🤔 Для скроллинга'
    MAIN_PAGE = "🔙 На главную"
    CANCEL = "❌ Отмена"
    AMOUNT_FOR_PAY = '💵 Оплатить {amount} USDT'
    BACK_IN_BOT = f"{BACK} {settings.NAME_BOT}"
    BACK_PROFILE = {BACK: 'profile'}
    BUY_WITH_DISCOUNT = "📉 Купить со скидкой {discount}%"



class CreatorMessages:
    def __init__(self,
                 text: Optional[str] = None,
                 buttons: Optional[Union[dict, list]] = None,
                 size: Optional[int] = 1):
        self.text: str = text or self._create_text()
        self.buttons: Optional[Union[dict, list]] = buttons or self._create_buttons()
        self.size = size

    def _create_text(self, *args, **kwargs) -> str:
        return ""

    def _create_buttons(self, *args, **kwargs) -> Optional[Union[dict, list]]:
        return []

    def __repr__(self):
        return f'{self.text}\n{self.buttons}\n{self.size}'


#  messages for start page

class Start(CreatorMessages):
    def __init__(self, username: Optional[str]):
        self.username = username
        super().__init__(size=2)

    def _create_text(self) -> str:
        return (f"👋 Привет, {self.username}\n\n"
                "<u>❗Обязательно ознакомься с правилами нашего магазина, можешь прочитать</u> "
                f"<a href='{settings.URL_RULES}'>👉 "
                "ТУТ</a>")

    def _create_buttons(self) -> Optional[Union[dict, list]]:
        return ['👨🏼‍💻 Профиль', '🔐 Аренда прокси',
                '🔤 Уникализатор', '🧑‍💻 Промокоды']


class UserNotMember(CreatorMessages):
    def __init__(self, text: Optional[str] = None):
        text = text or "👁 Для пользования ботом, тебе необходимо подписаться на канал ниже! 👇"
        super().__init__(text=text)

    def _create_buttons(self, *args, **kwargs) -> Optional[Union[dict, list]]:
        return {f'Подписаться {settings.CHAT_NAME}': settings.CHAT_SUB_LINK,
                '✅ Подписался': 'check_subscribe'}


class UserNotSubscribe(UserNotMember):
    def __init__(self):
        text = "❌ Вы меня не обманете! Тебе необходимо подписаться на канал ниже для пользования ботом! 👇"
        super().__init__(text=text)


class IfUserBlocked(CreatorMessages):
    def __init__(self):
        text = "❌ Администрация заблокировала вас в боте!"
        super().__init__(text=text)


class ForAdminAfterRegistration(CreatorMessages):
    def __init__(self):
        text = ("❗️Пользователь @{username}\n\n"
                "Только что зарегистрировался в боте!\n"
                f"{datetime.now().strftime('%d-%m-%Y %H:%M')}")
        super().__init__(text=text)


class AdminPanel(CreatorMessages):
    def __init__(self):
        text = "<b>🏦 МЕНЮ АДМИНИСТРАТОРА 🏦</b>"
        buttons = ['📨 Сделать рассылку', '❓ Информация о пользователе',
                   '📊 Статистика бота', '👑 Добавить администратора',
                   '💰 Добавить промокод', '⚙ Управление промокодами',
                   '⚙ Настройки фото']
        super().__init__(text=text, buttons=buttons, size=2)


# _______________________________________________________________________________________________________________________

# messages for profile page

class MainProfile(CreatorMessages):
    def __init__(self, user_data: dict):
        self.user_data = user_data
        buttons = {
            '🗄 Ваши покупки': 'purchases',
            '💰 Пополнить баланс': 'payment',
            '🗣 Написать администратору': 'msg_admin',
            '🏦 Сотрудничество и реклама': 'advertising'
        }
        super().__init__(buttons=buttons)

    def _create_text(self):
        return (f"<b>Профиль пользователя @{self.user_data['username']}\n\n"
                f"🏦 Ваш баланс: {self.user_data['balance']} RUB\n\n"
                f"🤌 Количество покупок: {self.user_data['purchase_count']}\n\n"
                f"💸 Доход от рефералов: {self.user_data['referral_income']}\n\n"
                f"👥 Всего ваших рефералов: {self.user_data['referral_count']}\n\n"
                f"🙋🏻‍♂️ Ваш id: {self.user_data['user_id']}\n\n"
                f"♨ Ваша реферальная ссылка: <code>{settings.HREF_REF}{self.user_data['user_id']}</code></b>\n\n"
                f"🤑 <b>Вы будете получать на баланс {settings.PERCENTAGE_FROM_REF * 100}% от пополнений "
                "ваших рефералов!</b>")


class UserPurchasesPage(CreatorMessages):
    def __init__(self, list_purchases: list):
        self.list_purchases: list = list_purchases
        super().__init__()

    def _create_buttons(self):
        buttons = {}
        self.size = 1
        if len(self.list_purchases) > 10:
            self.size = 2
            self.list_purchases = self.list_purchases[-10:]
        for item, purchase in enumerate(self.list_purchases):
            buttons[f'{item + 1}. {purchase.purchase_time.strftime("%d-%m-%Y")}'] = f'purchase_user:{purchase.id}'
        return buttons | ShortButton.BACK_PROFILE

    def _create_text(self):
        if self.list_purchases:
            return "<b>Вот ваши последние покупки.</b>"
        return "<b>У вас не было покупок... 😢</b>"


class ForSinglePurchase(CreatorMessages):
    def __init__(self, data_purchase: dict):
        buttons = {ShortButton.BACK: 'purchases'}
        self.d_p: dict = data_purchase
        super().__init__(buttons=buttons)

    def _create_text(self):
        if len(self.d_p) == 8:
            return ("Товар: {product_name}\n\n"
                    "Цена: {amount} RUB\n"
                    "Страна: {country}\n"
                    "Город: {city}\n"
                    "Данные: <code>{host}:{port}:{username}:{password}</code>"
                    ).format(**self.d_p)
        else:
            return ("Товар: {product_name}\n\n"
                    "Цена: {amount} RUB\n"
                    "Страна: {country}\n"
                    "Дата покупки: {purchase_time}\n"
                    "Дата окончания: {end_time}\n\n"
                    "HTTP: <code>{host}:{port}:{username}:{password}</code>\n"
                    "SOCKS5: <code>{host}:{port_socks}:{username}:{password}</code>").format(**self.d_p)


class ChoosePayment(CreatorMessages):
    def __init__(self):
        text = "<b>Вы берите систему для оплаты</b>"
        buttons = {'🪙 CryptoBot': 'cryptobot',
                   '💶 YooMoney': 'yoo_money',
                   '🚀 XRocket': 'xrocket',
                   ShortButton.BACK: "profile"}
        super().__init__(text=text, buttons=buttons)


class WriteToAdministration:
    to_admin = '<b>Напишите сообщение администратору</b>'
    about_adv = '<b>Напишите сообщение насчет сотрудничества</b>'
    message_send = '<b>Сообщение отправлено!</b>'
    back_profile = ShortButton.BACK_PROFILE















if __name__ == '__main__':
    print(IfUserBlocked.__dict__)
