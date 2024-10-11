from datetime import datetime
from typing import Any

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
    text: str = ''
    buttons = [] or {}
    size: int = 1

    @staticmethod
    def create_text(data: Any):
        pass

    @staticmethod
    def create_buttons(data: Any):
        pass


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


class AdminPanel(CreatorMessages):
    text = "<b>🏦 МЕНЮ АДМИНИСТРАТОРА 🏦</b>"
    buttons = ['📨 Сделать рассылку', '❓ Информация о пользователе',
               '📊 Статистика бота', '👑 Добавить администратора',
               '💰 Добавить промокод', '⚙ Управление промокодами',
               '⚙ Настройки фото']


# _______________________________________________________________________________________________________________________

# messages for profile page

class MainProfile(CreatorMessages):
    buttons = {
        '🗄 Ваши покупки': 'purchases',
        '💰 Пополнить баланс': 'payment',
        '🗣 Написать администратору': 'msg_admin',
        '🏦 Сотрудничество и реклама': 'advertising'
    }

    @staticmethod
    def create_text(user_data: dict):
        return (f"<b>Профиль пользователя @{user_data['username']}\n\n"
                f"🏦 Ваш баланс: {user_data['balance']} RUB\n\n"
                f"🤌 Количество покупок: {user_data['purchase_count']}\n\n"
                f"💸 Доход от рефералов: {user_data['referral_income']}\n\n"
                f"👥 Всего ваших рефералов: {user_data['referral_count']}\n\n"
                f"🙋🏻‍♂️ Ваш id: {user_data['user_id']}\n\n"
                f"♨ Ваша реферальная ссылка: <code>{settings.HREF_REF}{user_data['user_id']}</code></b>\n\n"
                f"🤑 <b>Вы будете получать на баланс {settings.PERCENTAGE_FROM_REF * 100}% от пополнений "
                "ваших рефералов!</b>")


class UserPurchasesPage(CreatorMessages):
    @staticmethod
    def create_buttons(list_purchases: list):
        buttons = {}
        size = 1
        if len(list_purchases) > 10:
            size = 2
            list_purchases = list_purchases[-10:]
        for item, purchase in enumerate(list_purchases):
            buttons[f'{item + 1}. {purchase.purchase_time.strftime("%d-%m-%Y")}'] = f'purchase_user:{purchase.id}'
        return buttons | ShortButton.BACK_PROFILE, size

    @staticmethod
    def create_text(list_purchases: list):
        if list_purchases:
            return "<b>Вот ваши последние покупки.</b>"
        return "<b>У вас не было покупок... 😢</b>"


class ForSinglePurchase(CreatorMessages):
    buttons = {ShortButton.BACK: 'purchases'}

    @staticmethod
    def create_text(data_purchase: dict):
        if len(data_purchase) == 8:
            return (f"Товар: {data_purchase['product_name']}\n\n"
                    f"Цена: {data_purchase['amount']} RUB\n"
                    f"Страна: {data_purchase['country']}\n"
                    f"Город: {data_purchase['city']}\n"
                    f"Данные: <code>{data_purchase['host']}:{data_purchase['port']}:{data_purchase['username']}:{data_purchase['password']}</code>"
                    )
        else:
            return (f"Товар: {data_purchase['product_name']}\n\n"
                    f"Цена: {data_purchase['amount']} RUB\n"
                    f"Страна: {data_purchase['country']}\n"
                    f"Дата покупки: {data_purchase['purchase_time']}\n"
                    f"Дата окончания: {data_purchase['end_time']}\n\n"
                    f"HTTP: <code>{data_purchase['host']}:{data_purchase['port']}:{data_purchase['username']}:{data_purchase['password']}</code>\n"
                    f"SOCKS5: <code>{data_purchase['host']}:{data_purchase['port_socks']}:{data_purchase['username']}:{data_purchase['password']}</code>")















if __name__ == '__main__':
    print(IfUserBlocked.__dict__)
