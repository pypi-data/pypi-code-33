from .core import PotOdds


class TestPotOdds:

    def setup(self):
        self.pot_odds = PotOdds(10, 5)

    def test_to_one(self):
        assert self.pot_odds.to_one() == 2

    def test_to_persent(self):
        assert self.pot_odds.to_persent(1) == 50

    def test_get_odds(self):
        assert abs(self.pot_odds.get_odds() - 33) < 0.5
