class UnderZeroError(Exception):
    def __init__(self):
        self.text = "<b><i>Вы ввели сумму равную или меньше нуля. Попробуйте еще раз!</i></b>"
        super().__init__(self.text)


class WrongAmountError(Exception):
    def __init__(self):
        self.text = "<b>Необходимо ввести число!</b>\n\n<i>100 или 100.0</i>"
        super().__init__(self.text)


class XRocketException(Exception):
    def __init__(self):
        self.text = "<b>С сервисом xRocket неполадки, попробуйте позже!</b>"
        super().__init__(self.text)
