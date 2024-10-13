from abc import ABC, abstractmethod
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


class CreatorMessages(ABC):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.size = 1

    @abstractmethod
    def text(self):
        pass

    @abstractmethod
    def buttons(self):
        pass

    def __repr__(self):
        return f'{self.text}\n{self.buttons}\n{self.size}'

    def __call__(self):
        return {"text": self.text(), "buttons": self.buttons(), "size": self.size}


#  messages for start page

class Start(CreatorMessages):
    def text(self) -> str:
        return (f"👋 Привет, {self.kwargs['username']}\n\n"
                "<u>❗Обязательно ознакомься с правилами нашего магазина, можешь прочитать</u> "
                f"<a href='{settings.URL_RULES}'>👉 "
                "ТУТ</a>")

    def buttons(self) -> Optional[Union[dict, list]]:
        self.size = 2
        return ['👨🏼‍💻 Профиль', '🔐 Аренда прокси',
                '🔤 Уникализатор', '🧑‍💻 Промокоды']


class UserNotMember(CreatorMessages):
    def text(self):
        return "👁 Для пользования ботом, тебе необходимо подписаться на канал ниже! 👇"

    def buttons(self):
        return {f'Подписаться {settings.CHAT_NAME}': settings.CHAT_SUB_LINK,
                '✅ Подписался': 'check_subscribe'}


class UserNotSubscribe(UserNotMember):
    def text(self):
        return "❌ Вы меня не обманете! Тебе необходимо подписаться на канал ниже для пользования ботом! 👇"

    def buttons(self):
        super().buttons()


class IfUserBlocked(CreatorMessages):
    def text(self):
        return "❌ Администрация заблокировала вас в боте!"

    def buttons(self):
        return None


class ForAdminAfterRegistration(CreatorMessages):
    def text(self):
        username = self.kwargs['username']
        return (f"❗️Пользователь @{username}\n\n"
                "Только что зарегистрировался в боте!\n"
                f"{datetime.now().strftime('%d-%m-%Y %H:%M')}")

    def buttons(self):
        return None


class AdminPanel(CreatorMessages):
    def text(self):
        return "<b>🏦 МЕНЮ АДМИНИСТРАТОРА 🏦</b>"

    def buttons(self):
        self.size = 2
        return ['📨 Сделать рассылку', '❓ Информация о пользователе',
                   '📊 Статистика бота', '👑 Добавить администратора',
                   '💰 Добавить промокод', '⚙ Управление промокодами',
                   '⚙ Настройки фото']


# _______________________________________________________________________________________________________________________

# messages for profile page

class MainProfile(CreatorMessages):

    def text(self):
        user_data = self.kwargs['user_data']
        return (f"<b>Профиль пользователя @{user_data['username']}\n\n"
                f"🏦 Ваш баланс: {user_data['balance']} RUB\n\n"
                f"🤌 Количество покупок: {user_data['purchase_count']}\n\n"
                f"💸 Доход от рефералов: {user_data['referral_income']}\n\n"
                f"👥 Всего ваших рефералов: {user_data['referral_count']}\n\n"
                f"🙋🏻‍♂️ Ваш id: {user_data['user_id']}\n\n"
                f"♨ Ваша реферальная ссылка: <code>{settings.HREF_REF}{user_data['user_id']}</code></b>\n\n"
                f"🤑 <b>Вы будете получать на баланс {settings.PERCENTAGE_FROM_REF * 100}% от пополнений "
                "ваших рефералов!</b>")

    def buttons(self):
        return {
            '🗄 Ваши покупки': 'purchases',
            '💰 Пополнить баланс': 'payment',
            '🗣 Написать администратору': 'msg_admin',
            '🏦 Сотрудничество и реклама': 'advertising'
        }


class UserPurchasesPage(CreatorMessages):
    def text(self):
        if self.kwargs['list_purchases']:
            return "<b>Вот ваши последние покупки.</b>"
        return "<b>У вас не было покупок... 😢</b>"

    def buttons(self):
        list_purchases = self.kwargs['list_purchases']
        buttons = {}
        self.size = 1
        if len(list_purchases) > 10:
            self.size = 2
            list_purchases = list_purchases[-10:]
        for item, purchase in enumerate(list_purchases):
            buttons[f'{item + 1}. {purchase.purchase_time.strftime("%d-%m-%Y")}'] = f'purchase_user:{purchase.id}'
        return buttons | ShortButton.BACK_PROFILE




class ForSinglePurchase(CreatorMessages):

    def text(self):
        data_purchase = self.kwargs['data_purchase']
        if len(data_purchase) == 8:
            return ("Товар: {product_name}\n\n"
                    "Цена: {amount} RUB\n"
                    "Страна: {country}\n"
                    "Город: {city}\n"
                    "Данные: <code>{host}:{port}:{username}:{password}</code>"
                    ).format(**data_purchase)
        else:
            return ("Товар: {product_name}\n\n"
                    "Цена: {amount} RUB\n"
                    "Страна: {country}\n"
                    "Дата покупки: {purchase_time}\n"
                    "Дата окончания: {end_time}\n\n"
                    "HTTP: <code>{host}:{port}:{username}:{password}</code>\n"
                    "SOCKS5: <code>{host}:{port_socks}:{username}:{password}</code>").format(**data_purchase)

    def buttons(self):
        return {ShortButton.BACK: 'purchases'}


class ChoosePayment(CreatorMessages):
    def text(self):
        return "<b>Вы берите систему для оплаты</b>"

    def buttons(self):
        return {'🪙 CryptoBot': 'cryptobot',
                '💶 YooMoney': 'yoomoney',
                '🚀 xRocket': 'xrocket',
                   ShortButton.BACK: "profile"}


class WriteToAdministration:
    to_admin = '<b>Напишите сообщение администратору</b>'
    about_adv = '<b>Напишите сообщение насчет сотрудничества</b>'
    message_send = '<b>Сообщение отправлено!</b>'
    back_profile = ShortButton.BACK_PROFILE


# _______________________________________________________________________________________________________________________

# payments page

class ChoicePayment:
    cryptobot = ('<b>♻️ Оплата будет производиться через</b> <a href="https://t.me/CryptoBot">CryptoBot</a> \n'
                 '<b>❗ Валюта для оплаты:</b> <i>RUB</i>\n\n'
                 '✍️ <b>Введите сумму пополнения:</b>')
    yoomoney = ('<b>♻️ Оплата будет производиться через</b> <a href="https://yoomoney.ru">YooMoney</a> \n'
                '<b>❗ Валюта для оплаты:</b> <i>RUB</i>\n\n'
                '✍️ <b>Введите сумму пополнения:</b>')
    xrocket = ('<b>♻️ Оплата будет производиться через</b> <a href="https://t.me/@tonRocketBot">xRocket</a> \n'
               '<b>❗ Валюта для оплаты:</b> <i>RUB</i>\n\n'
               '✍️ <b>Введите сумму пополнения:</b>')
    back_keyboard = {ShortButton.BACK: 'payment'}
















if __name__ == '__main__':
    print(IfUserBlocked.__dict__)
