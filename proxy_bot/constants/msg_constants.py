from datetime import datetime
from typing import Optional, Union

from proxy_bot.constants.load_constants import Constant
from proxy_bot.db.models import ProxyWork, ProxySort
from proxy_bot.helpers import countries_dict, pagination
from proxy_bot.settings import settings


class ShortButton:
    BACK = '🔙 Назад'
    work = '👨‍💻 Work mode'
    sort = '🗺 Work mode (sort)'
    scrolling = '🤔 Scrolling'
    MAIN_PAGE = "🔙 На главную"
    CANCEL = "❌ Отмена"
    AMOUNT_FOR_PAY = '💵 Оплатить {amount} USDT'
    BACK_IN_BOT = f"{BACK} {settings.NAME_BOT}"
    BACK_PROFILE = {BACK: 'profile'}
    BUY_WITH_DISCOUNT = "📉 Купить со скидкой {discount}%"
    BACK_SORT = {BACK: "sorted_work"}
    PROXYLINE_WORK = {"✅ Счет пополнен!": "proxyline_work"}


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
        self.photo = Constant.PHOTOS.get('default', False)
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
        self.photo = Constant.PHOTOS.get('menu', False)
        return (f"👋 Привет, {self.kwargs['username']}\n\n"
                "<u>❗Обязательно ознакомься с правилами нашего магазина, можешь прочитать</u> "
                f"<a href='{settings.URL_RULES}'>👉 "
                "ТУТ</a>")

    def create_buttons(self) -> Optional[Union[dict, list]]:
        self.size = 2
        return [MenuButton.PROFILE, MenuButton.PROXIES,
                MenuButton.UNIQUE, MenuButton.DISCOUNT]


class UserNotMember(CreatorMessages):
    photo = Constant.PHOTOS.get('default', False)
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
    size = 2

    def create_text(self) -> Optional[str]:
        self.photo = Constant.PHOTOS.get('menu', False)
        return "<b>🏦 МЕНЮ АДМИНИСТРАТОРА 🏦</b>"

    def create_buttons(self) -> Optional[Union[list, dict]]:
        self.size = 2
        return ['📨 Сделать рассылку', '❓ Информация о пользователе',
                '📊 Статистика бота', '👑 Добавить администратора',
                '💰 Добавить промокод', '⚙ Управление промокодами',
                '⚙ Настройки фото']




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
    def create_text(self) -> Optional[str]:
        self.photo = False
        return ('<b>✍ Введите текст для его уникализации:</b>\n\n'
                '<i>Вы можете отправлять текст постоянно</i>')


class GoodUniqueMessage(CreatorMessages):
    def create_text(self):
        self.photo = False
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


class ChooseSortProxy(CreatorMessages):
    def create_text(self) -> Optional[str]:
        return (f'🏦 Стоимость прокси: <u><b>{settings.COUNTRY_PRICE_PROXY} рублей.</b></u>\n'
                '⏲ Жизнь прокси: <u><b>5 часов.</b></u>\n\n'
                'Выберите страну прокси:')

    def create_buttons(self) -> Optional[Union[list, dict]]:
        buttons = {}
        if len(Constant.PROXIES_SORT) > 3:
            self.size = 2
        else:
            self.size = 1
        for key, value in Constant.PROXIES_SORT.items():
            buttons[f'{countries_dict(key)[0:2]} - {len(value)} шт.'] = f"sort_country:{key}"
        return buttons | {ShortButton.BACK: "shop"}


class ChooseLenSortProxy(CreatorMessages):
    def create_text(self) -> Optional[str]:
        country_code = self.kwargs['country_code']
        return (f"Доступное количество прокси для {countries_dict(country_code)} - "
                f"{len(Constant.PROXIES_SORT.get(country_code, 0))}")

    def create_buttons(self) -> Optional[Union[list, dict]]:
        self.size = 2
        country_code = self.kwargs['country_code']
        items = [1, 3, 5, 7, 10, 15]
        buttons = {}
        for i in items:
            if 0 < len(Constant.PROXIES_SORT.get(country_code, 0)) >= i:
                buttons[f'{i} шт.'] = f'sort_proxy:{i}'
        return buttons | {ShortButton.BACK: f"sorted_work"}


class NotProxyMessage:
    text = "В данный момент прокси нет в наличии!"
    text_no_work_proxy = "<b>Прокси закончились в WorkMode!!!</b>"
    text_no_sort_proxy = "<b>Прокси закончились в WorkMode (sort)!!!</b>"
    work_proxy_death = f"<b>Прокси {ShortButton.work} перестали работать</b>"
    sort_proxy_death = f"<b>Прокси {ShortButton.sort} перестали работать</b>"


class CheckingProxyText:
    text = "<b>Идет проверка работоспособности прокси!</b>"
    broken = "<b>❌ Прокси сломались!❗️</b>"


class ProxyMessage(CreatorMessages):
    def create_text(self) -> Optional[str]:
        proxy_list: list[Union[ProxyWork, ProxySort]] = self.kwargs['proxy_list']
        if len(proxy_list) > 7:
            return "<b>Ввиду большого количества, прокси отправлены файлом!</b>"
        else:
            message = "<b>Вот ваши прокси:\n</b>"
            for proxy in proxy_list:
                message += f"\n<code>{proxy.host}:{proxy.port}:{proxy.username}:{proxy.password}</code>"
            return message


class MessageToAdminAfterBuy(CreatorMessages):
    def create_text(self) -> Optional[str]:
        username = self.kwargs.get('username')
        category = self.kwargs.get('category')
        count = self.kwargs.get('count')
        price = self.kwargs.get('price')
        return (f"❗️Пользователь @{username}\n\n"
                "<b><u>Покупка прокси</u></b>\n\n"
                f"<u>Категория</u>: <i>{category}</i>\n"
                f"<u>Количество прокси</u>: <i>{count}</i>\n"
                f"<u>Сумма</u>: <i>{price} рублей</i>\n"
                f"<u>Дата</u>: {datetime.now().strftime('%d-%m-%Y %H:%M')}")


class ProxyLineNoPlan:
    for_error = "По выбранному тарифу прокси нет!"
    for_not_proxy = "Тарифных планов пока нет!"


class ChooseTypeProxy(CreatorMessages):
    text = ('<b>❗️ Выберите тип прокси:\n'
            '<u>IPv4 Privat</u> - дорогие и качественные прокси,\n'
            'подходят для длительного использования, например '
            'для ворка Facebook 🇪🇺 \n\n'
            '<u>IPv6 Privat</u> - дешевые прокси,\n'
            'отличный выбор для анонимной работе в браузере,\n'
            'средняя цена 12 рублей</b>')

    def create_buttons(self) -> Optional[Union[list, dict]]:
        self.size = 2
        return {
            '🌍 IPv4 private': 'ipv4',
            '🌍 IPv6 private': 'ipv6',
            ShortButton.BACK: 'shop',
        }


class MainPageProxyLine(CreatorMessages):
    def create_text(self) -> Optional[str]:
        ip_version = self.kwargs.get("ip_version")
        return (f'Вы выбрали 🌍 IPv{ip_version} private\n\n'
                '❗️ Важная информация!\n\n'
                'Из-за сложившейся в мире ситуации наблюдаются следующие ограничения:\n'
                'Большинство RU прокси не работают из Украины\n'
                'Эти ограничения от нас не зависят, их ввели провайдеры стран.\n'
                'Используйте VPN третьей страны между вашим устройством и прокси.'
                'Спасибо за понимание. Всем мира!\n\n'
                'Выберите страну прокси:')

    def create_buttons(self) -> Optional[Union[list, dict]]:
        ip_version = self.kwargs.get("ip_version")
        if ip_version == 4:
            callback_data = self.kwargs['callback_data']
            back_page = self.kwargs['back_page']
            return pagination(callback_data=callback_data, back_page=back_page)
        else:
            self.size = 2
            return {f'{countries_dict("ru")}': 'country:ru',
                    f'{countries_dict("us")}': 'country:us',
                    ShortButton.BACK: 'scrolling'}


class ChoiceCountry(CreatorMessages):
    def create_text(self) -> Optional[str]:
        new_order = self.kwargs.get("new_order")
        return (f"Вы выбрали: 🌍 IPv{new_order.ip_version}\n"
                f"Страна: {countries_dict(new_order.country)}\n\n"
                "❗️ Выберите период пользования (в днях)!")

    def create_buttons(self) -> Optional[Union[list, dict]]:
        new_order = self.kwargs.get("new_order")
        self.size = 2
        return {
            '5': 'period:5',
            '10': 'period:10',
            '20': 'period:20',
            '30': 'period:30',
            ShortButton.BACK: f'ipv{new_order.ip_version}:0',
            ShortButton.MAIN_PAGE: 'shop'
        }


class PreviewMessage(CreatorMessages):
    def create_text(self) -> Optional[str]:
        new_order = self.kwargs.get("new_order")
        price = self.kwargs.get("price")
        return ('Ваш заказ:\n\n'
                f'🗺 Страна: {countries_dict(new_order.country)}\n'
                f'🌐 Тип: IPv{new_order.ip_version} private\n'
                f'🕖 Срок аренды: {new_order.period} дней\n'
                f'🤌 Количество: {new_order.quantity} шт.\n\n'
                f'🧾 Цена: {price} RUB\n')

    def create_buttons(self) -> Optional[Union[list, dict]]:
        discount = self.kwargs.get("discount")
        new_order = self.kwargs.get("new_order")
        keyboard = {"🤑 Купить": "buy_proxy"}
        discount_button = {}
        if discount is not None:
            discount_button = {"Купить со скидкой": "buy_with_discount"}
        back_button = {"🔙 К выбору страны": f"ipv{new_order.ip_version}",
                       ShortButton.MAIN_PAGE: "scrolling"}
        return keyboard | discount_button | back_button


class ProxyLineWork(CreatorMessages):
    text = "<b>Теперь пользователи могут покупать прокси!</b>"




if __name__ == '__main__':
    print(IfUserBlocked.__dict__)
