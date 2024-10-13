class UnderZeroError(Exception):
    def __init__(self):
        self.text = "Вы ввели сумму равную или меньше нуля. Попробуйте еще раз!"
        super().__init__(self.text)


class WrongAmountError(Exception):
    def __init__(self):
        self.text = "<b>Необходимо ввести число!</b>\n\n<i>100 или 100.0</i>"
        super().__init__(self.text)
