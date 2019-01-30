import numpy as np
import pandas as pd

from .orthotope import orthotope_c

class normal_form_c:
    def __init__ (self, players, payoff_tensor):
        self.player_list = list (players.keys ())
        self.nof_player = len (self.player_list)
        self.axes = {
            ** players,
            "payoff": self.player_list,
        }
        self.data_tope = orthotope_c (self.axes, payoff_tensor)

    # player: str
    # action: str
    # pure_strategy: pd.Series <player, action>

    def pure_strategy_c (self, pure_strategy):
        return pd.Series (
            pure_strategy,
            index = self.player_list)

    def proj (self, pure_strategy):
        pure_strategy = self.pure_strategy_c (pure_strategy)
        return self.data_tope.proj (pure_strategy)

    def pure_responses (self, pure_strategy):
        pure_strategy = self.pure_strategy_c (pure_strategy)
        miss = pure_strategy [ pure_strategy.isna () ]
        player_list = miss.keys ()
        assert len (player_list) == 1
        return self.proj (pure_strategy) .to_data_frame ()

    def best_pure_responses (self, pure_strategy):
        pure_responses = self.pure_responses (pure_strategy)
        player = pure_responses.index.names [0]
        grouped_responses = pure_responses.groupby (player)
        _value, df = list (grouped_responses) [-1]
        return df

    # # def pure_nash_equilibrium (self):
    # #     return

    # # def pure_dominant (self, pure_strategy1, pure_strategy2):
    # #     return

    # # def dominant_pure_strategy (self):
    # #     return
