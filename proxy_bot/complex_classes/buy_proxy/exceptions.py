from proxy_bot.constants.msg_constants import ProxyLineNoPlan, ShortButton


class UserNotMoneyError(Exception):
    def __init__(self):
        self.text = "На вашем балансе не хватает средств для покупки!"
        super().__init__(self.text)


class NotEnoughProxyError(Exception):
    def __init__(self, count_proxy_db: int):
        self.text = f'Сейчас прокси не хватает. В наличии {count_proxy_db} шт.'
        super().__init__(self.text)


class NotProxyInBaseError(Exception):
    def __init__(self):
        self.text = "Прокси в наличии нет."
        super().__init__(self.text)


class BadProxyError(Exception):
    pass


class ProxyDeathError(Exception):
    def __init__(self):
        self.text = "К сожалению прокси перестали работать. Сообщение отправлено администрации!"
        super().__init__(self.text)


class NoPlanError(Exception):
    def __init__(self):
        self.text = ProxyLineNoPlan.for_error
        super().__init__(self.text)


class NoMoneySiteError(Exception):
    def __init__(self, balance: float):
        self.text_admin = ("На сайте https://proxyline.net не хватает денег для покупки прокси!\n\n"
                           f"Баланс: {balance} RUB\n\n"
                           "❌ Не удаляйте это сообщение до тех пор, пока не пополните баланс!"
                           "После пополнения баланса, нажмите на кнопку ниже!")
        self.buttons = ShortButton.PROXYLINE_WORK
        self.text_user = "Тарифных планов пока нет!"
        super().__init__(self.text_admin, self.text_user)


class UserNotMoneyProxyLineError(Exception):
    def __init__(self, amount: float):
        self.text = f"На вашем балансе не хватает {amount} RUB для покупки такого количества прокси."
        super().__init__(self.text)
