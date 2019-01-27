from potodds import PotOdds


def main():
    pot = int(input('Введите банк'))
    bet = int(input('Введите ставку'))

    result = PotOdds(pot, bet).get_odds()
    print(result)


if __name__ == '__main__':
    main()