class PotOdds:
    """
    Класс для расчета шансов банка
    """

    def __init__(self, pot, bet):
        """
        :param pot: весь банк
        :param bet: ставка которую надо колировать
        """
        self.pot = pot
        self.bet = bet

    def to_one(self):
        # считаем отношение банка к ставке
        # банк делим на ставку
        # весь банк делим на ставку
        # Это отношение вида 1 : 5
        return self.pot / self.bet

    def to_persent(self, to_one):
        """
        Приводим отношение вида 1 : 5 к процентам
        :param to_one: число x в отношении 1 : x
        :return: шансы банка в процентах
        """
        return 100 / (1 + to_one)

    def get_odds(self):
        """
        Вычисление шансов банка
        :return: Шансы банка
        """
        to_one = self.to_one()
        return self.to_persent(to_one)
