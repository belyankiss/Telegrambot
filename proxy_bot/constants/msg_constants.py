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


class MenuButton:
    PROFILE = '👨🏼‍💻 Профиль'
    UNIQUE = '🔤 Уникализатор'
    PROXIES = '🔐 Аренда прокси'
    DISCOUNT = '🧑‍💻 Промокоды'


class CreatorMessages:
    text: Optional[str] = None
    buttons: Optional[Union[list, dict]] = None
    size: int = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.size = 1
        self.text = self.create_text() or type(self).text
        self.buttons = self.create_buttons() or type(self).buttons

    def create_text(self) -> Optional[str]:
        return None

    def create_buttons(self) -> Optional[Union[list, dict]]:
        return None

    def __repr__(self):
        return f'{self.text}\n{self.buttons}\n{self.size}'

    def __call__(self):
        size = type(self).size if type(self).size is not None else self.size
        return {"text": self.text, "buttons": self.buttons, "size": size}


#  messages for start page

class Start(CreatorMessages):
    def create_text(self) -> str:
        return (f"👋 Привет, {self.kwargs['username']}\n\n"
                "<u>❗Обязательно ознакомься с правилами нашего магазина, можешь прочитать</u> "
                f"<a href='{settings.URL_RULES}'>👉 "
                "ТУТ</a>")

    def create_buttons(self) -> Optional[Union[dict, list]]:
        self.size = 2
        return [MenuButton.PROFILE, MenuButton.PROXIES,
                MenuButton.UNIQUE, MenuButton.DISCOUNT]


class UserNotMember(CreatorMessages):
    text = "👁 Для пользования ботом, тебе необходимо подписаться на канал ниже! 👇"

    buttons = {f'Подписаться {settings.CHAT_NAME}': settings.CHAT_SUB_LINK,
                '✅ Подписался': 'check_subscribe'}


class UserNotSubscribe(CreatorMessages):
    text = "❌ Вы меня не обманете! Тебе необходимо подписаться на канал ниже для пользования ботом! 👇"

    buttons = UserNotMember.buttons



class IfUserBlocked(CreatorMessages):
    text = "❌ Администрация заблокировала вас в боте!"



class ForAdminAfterRegistration(CreatorMessages):
    def create_text(self):
        username = self.kwargs['username']
        return (f"❗️Пользователь @{username}\n\n"
                "Только что зарегистрировался в боте!\n"
                f"{datetime.now().strftime('%d-%m-%Y %H:%M')}")



class AdminPanel(CreatorMessages):
    text = "<b>🏦 МЕНЮ АДМИНИСТРАТОРА 🏦</b>"

    buttons = ['📨 Сделать рассылку', '❓ Информация о пользователе',
                   '📊 Статистика бота', '👑 Добавить администратора',
                   '💰 Добавить промокод', '⚙ Управление промокодами',
                   '⚙ Настройки фото']
    size = 2



# _______________________________________________________________________________________________________________________

# messages for profile page

class MainProfile(CreatorMessages):

    def create_text(self):
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

    buttons = {
            '🗄 Ваши покупки': 'purchases',
            '💰 Пополнить баланс': 'payment',
            '🗣 Написать администратору': 'msg_admin',
            '🏦 Сотрудничество и реклама': 'advertising'
        }


class UserPurchasesPage(CreatorMessages):
    def create_text(self):
        if self.kwargs['list_purchases']:
            return "<b>Вот ваши последние покупки.</b>"
        return "<b>У вас не было покупок... 😢</b>"

    def create_buttons(self):
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

    def create_text(self):
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

    buttons = {ShortButton.BACK: 'purchases'}


class ChoosePayment(CreatorMessages):
    text = "<b>Вы берите систему для оплаты</b>"

    buttons = {'🪙 CryptoBot': 'cryptobot',
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

class ChoicePayment(CreatorMessages):
    def create_text(self):
        if self.kwargs['payment'] == 'cryptobot':
            return ('<b>♻️ Оплата будет производиться через</b> <a href="https://t.me/CryptoBot">CryptoBot</a> \n'
                    '<b>❗ Валюта для оплаты:</b> <i>RUB</i>\n\n'
                    '✍️ <b>Введите сумму пополнения:</b>')
        elif self.kwargs['payment'] == 'yoomoney':
            return ('<b>♻️ Оплата будет производиться через</b> <a href="https://yoomoney.ru">YooMoney</a> \n'
                    '<b>❗ Валюта для оплаты:</b> <i>RUB</i>\n\n'
                    '✍️ <b>Введите сумму пополнения:</b>')
        else:
            return ('<b>♻️ Оплата будет производиться через</b> <a href="https://t.me/@tonRocketBot">xRocket</a> \n'
                    '<b>❗ Валюта для оплаты:</b> <i>RUB</i>\n\n'
                    '✍️ <b>Выберите монету для оплаты:</b>')

    def create_buttons(self):
        back_payment_button = {ShortButton.BACK: 'payment'}
        if self.kwargs['payment'] == 'cryptobot' or self.kwargs['payment'] == 'yoomoney':
            return back_payment_button
        else:
            self.size = 2
            x_buttons = {}
            currencies = ["XROCK", "TONCOIN", "BTC", "USDT", "TRX", "ETH", "BNB"]
            for cur in currencies:
                x_buttons[cur] = f'x_cur:{cur}'
            return x_buttons | back_payment_button


class ForXrocket(CreatorMessages):
    def create_text(self):
        return ('<b>♻️ Оплата будет производиться через</b> <a href="https://t.me/@tonRocketBot">xRocket</a> \n'
                f'<b>❗ Валюта для оплаты:</b> <i>{self.kwargs['currency']}</i>\n\n'
                '✍️ <b>Введите сумму пополнения:</b>')

    buttons = {ShortButton.BACK: 'xrocket'}


class PaymentMessage(CreatorMessages):
    def create_text(self):
        amount = self.kwargs["amount"]
        currency = self.kwargs.get("currency")
        if currency is None:
            currency = "RUB"
        return f"<b>Оплатите {amount} {currency} по кнопке ниже!</b>"

    def create_buttons(self):
        url = self.kwargs["invoice_url"]
        amount = self.kwargs["amount"]
        currency = self.kwargs.get("currency")
        if currency is None:
            currency = "RUB"
        return {f"Оплатить {amount} {currency}": url,
                ShortButton.BACK: "payment"}


class UpBalance(CreatorMessages):

    def create_text(self):
        amount = self.kwargs['amount']
        return f"<b>Ваш баланс успешно пополнен на сумму {amount} RUB</b>"

    buttons = ShortButton.BACK_PROFILE


class NoPayment(CreatorMessages):
    text = "<b>По какой-то причине ваш платеж не прошел или не был оплачен.</b>"



# _______________________________________________________________________________________________________________________

# unique_page_messages

class MainMessageUnique(CreatorMessages):
    text = ('<b>✍ Введите текст для его уникализации:</b>\n\n'
                '<i>Вы можете отправлять текст постоянно</i>')


class GoodUniqueMessage(CreatorMessages):

    def create_text(self):
        counter = self.kwargs.get('counter', False)
        unique_text = self.kwargs['unique_text']
        if counter:
            return (f'<b>Уникализированный текст - {counter}</b>\n\n'
                    f'<code>{unique_text}</code>')
        return ('<b>Уникализированный текст</b>\n\n'
                f'<code>{unique_text}</code>')

    buttons = {'❔ Переуникализировать?': 'unique_again'}


class WrongUniqueMessage(CreatorMessages):
    text = '<b>Вы должны были отправить текст!!!</b>'




# _______________________________________________________________________________________________________________________

# Discount page

class GetDiscountNameMessage(CreatorMessages):
    text = '<b>✍ Введите промокод на скидку: </b>'




class DiscountActivateSuccess(CreatorMessages):

    def create_text(self):
        percentage = self.kwargs['percentage'] * 100
        return f"Вы активировали скидку {percentage}%!"


# _______________________________________________________________________________________________________________________

# Proxy page

class MainProxyPage(CreatorMessages):

    def create_text(self):
        return ('<b>❗️ Выберите тип прокси:</b>\n\n'
                '👨‍💻 <u><b>Work mode</b></u> - <i>отлично подходят для ворка 🇪🇺 Fiverr  и '
                'других подобных площадок где важна чистота прокси, '
                f'средняя цена <u>{settings.PRICE_PROXY} рублей </u>за прокси.</i>\n\n '
                f'🗺 <u><b>Work mode (sort)</b></u> - <i>стоят дороже, но есть возможность выбрать страну '
                f'прокси. '
                f'Средняя цена <u>{settings.COUNTRY_PRICE_PROXY} рублей </u>за прокси.</i>\n\n'
                '🤔 <u><b>Scrolling</b></u> - <i>Прокси которые можно взять на длительный срок, '
                'чистые и анонимные, подходят для работы в браузерах и для посещения заблокированных сайтов.</i>')

    buttons = {'👨‍💻 Work mode': 'working',
               '🗺 Work mode (sort)': 'sorted_work',
               '🤔 Scrolling': 'scrolling'}


class ChooseWorkProxy(CreatorMessages):
    text = (f'🏦 Стоимость прокси: <u><b>{settings.PRICE_PROXY} рублей.</b></u>\n'
            '⏲ Жизнь прокси: <u><b>5 часов.</b></u>\n\n'
            'Выберите необходимое количество прокси:')

    def create_buttons(self):
        self.size = 2
        items = [1, 3, 5, 7, 10, 15]
        buttons = {}
        for i in items:
            buttons[f'{i} шт.'] = f'work_proxy:{i}'
        return buttons | {ShortButton.BACK: 'shop'}


class NotProxyMessage:
    text = "В данный момент прокси нет в наличии!"
    text_for_admin = "<b>Прокси закончились в WorkMode!!!</b>"


if __name__ == '__main__':
    print(IfUserBlocked.__dict__)
