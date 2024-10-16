class NotDiscountTextError(Exception):
    def __init__(self):
        self.text = '<b>Вы должны были отправить промокод!!!</b>'
        super().__init__(self.text)


class DiscountNotInBaseError(Exception):
    def __init__(self):
        self.text = "<b>Такого промокода не существует!</b>"
        super().__init__(self.text)


class UserHaveDiscountError(Exception):
    def __init__(self, discount: float):
        self.text = f"<b>У вас есть не активированная скидка размером {discount * 100} %</b>"
        super().__init__(self.text)


class DiscountWasActivatedError(Exception):
    def __init__(self):
        self.text = "<b>Вы уже активировали эту скидку!!!</b>"
        super().__init__(self.text)


class NotActivatesError(Exception):
    def __init__(self):
        self.text = "<b>Количество активаций этого купона закончилось!!!</b>"
        super().__init__(self.text)
