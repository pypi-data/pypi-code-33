from collections import namedtuple
from itertools import chain


class BallDatasetHandler:
    _train_tuple = namedtuple("TRAIN", ["LEIPZIG", "NAGOYA", "IRAN", "MONTREAL", "BITBOTSLAB",
                                        "CHALLENGE_2018",
                                        "ALL"])

    _data_leipzig = ["bitbots-set00-01", "bitbots-set00-02", "bitbots-set00-03", "bitbots-set00-04",
                     "bitbots-set00-05", "bitbots-set00-06", "bitbots-set00-07", "bitbots-set00-08",
                     "bitbots-set00-09", "bitbots-set00-10", "bitbots-set00-11", "bitbots-set00-12",
                     "bitbots-set00-13", "bitbots-set00-14", "bitbots-set00-15"]

    _data_nagoya = ["euro-ball-game-1",
                    "sequences-euro-ball-robot-1",
                    "sequences-jasper-euro-ball-1",
                    "sequences-jasper-kicking-euro-ball",
                    "sequences-misc-ball-1",
                    "sequences-misc-ball-robot-1"]
    _data_nagoya = ["2017_nagoya/" + e for e in _data_nagoya]

    _data_montreal = ["bitbots-fifa18-high-res-02",
                      "bitbots-montreal-ball-close",
                      "montreal-game01",
                      "montreal-game02",
                      "montreal-game03",
                      "montreal-game04",
                      "montreal-game05",
                      "montreal-game06",
                      "montreal-game07",
                      "montreal-game08",
                      "montreal-game09",
                      ]
    _data_montreal = ["2018_montreal/" + e for e in _data_montreal]

    _data_iran = ["bitbots-2018-iran-01",
                  "bitbots-2018-iran-02",
                  "bitbots-2018-iran-03",
                  "bitbots-2018-iran-04",
                  "bitbots-2018-iran-05",
                  "bitbots-2018-iran-06",
                  "bitbots-2018-iran-game-01-mrl-bitbots"]
    _data_iran = ["2018_iran/" + e for e in _data_iran]

    _data_bitbotslab = ["bitbots-fifa18-high-res-01",
                        "bitbots-fifa18-davros-01"]
    _data_bitbotslab = ["2018_bitbotslab/" + e for e in _data_bitbotslab]

    _test_nagoya_game_02 = "test-nagoya-game-02"
    _test_wolves_01 = "test-wolves-01"
    _test_2018_iran_minibot_20 = ["2018_iran/bitbots-2018-iran-20-minibot"]

    _test_bitbotslab_robot_concealed = ["euro-ball-robot-concealed"]
    _test_bitbotslab_robot_concealed = ["bitbots-lab/" + e for e in _test_bitbotslab_robot_concealed]

    _noised_test_nagoya_game_02 = "noised-test-nagoya-game-02"
    _noised_test_wolves_01 = "noised-test-wolves-01"

    _noised_test_real_01 = "test-blur-real-01"

    TRAIN = _train_tuple(LEIPZIG=_data_leipzig,
                         NAGOYA=_data_nagoya,
                         IRAN=_data_iran,
                         MONTREAL=_data_montreal,
                         BITBOTSLAB=_data_bitbotslab,
                         CHALLENGE_2018=[e for e in chain(_data_leipzig, _data_nagoya, _data_iran, _data_bitbotslab)],
                         ALL=[e for e in chain(_data_leipzig, _data_nagoya, _data_iran, _data_bitbotslab,
                                               _data_montreal)])

    TEST_NAGOYA_GAME_02 = [_test_nagoya_game_02]
    TEST_WOLVES_01 = [_test_wolves_01]
    TEST_BITBOTSLAB_ROBOT_CONCEALED = _test_bitbotslab_robot_concealed
    TEST_2018_IRAN_MINIBOT_20 = _test_2018_iran_minibot_20

    TEST_CHALLENGE_2018 = [_test_nagoya_game_02, _test_wolves_01]

    TEST_ALL = [_test_nagoya_game_02, _test_wolves_01]

    NOISED_TEST_NAGOYA_GAME_02 = [_noised_test_nagoya_game_02]
    NOISED_TEST_WOLVES_01 = [_noised_test_wolves_01]

    NOISED_TEST_REAL_01 = [_noised_test_real_01]

    NOISED_TEST_CHALLENGE_2018 = [_noised_test_nagoya_game_02, _noised_test_wolves_01]

    NOISED_TEST_ALL = [_noised_test_nagoya_game_02, _noised_test_wolves_01]


class NegativeBallDatasetHandler:
    _data_tuple = namedtuple("DATATUPLE", ["LEIPZIG", "NAGOYA", "BITBOTSLAB", "ALL"])

    _data_leipzig = ["cnn-training-negative-leipzig1"]

    _data_nagoya = ["negative-01"]
    _data_nagoya = ["2017_nagoya/" + e for e in _data_nagoya]

    _data_bitbotslab = ["negative01"]
    _data_bitbotslab = ["2018_bitbotslab/" + e for e in _data_bitbotslab]

    DATA = _data_tuple(LEIPZIG=_data_leipzig,
                       NAGOYA=_data_nagoya,
                       BITBOTSLAB=_data_bitbotslab,
                       ALL=[e for e in chain(_data_leipzig, _data_nagoya, _data_bitbotslab)])


class RandomUnlabeledDatasetHandler:
    _data_tuple = namedtuple("DATATUPLE", ["NAGOYA", "BITBOTSLAB", "ALL"])

    _data_nagoya = ["random-unlabeled-01",
                    "random-unlabeled-02",
                    "random-unlabeled-03",
                    "random-unlabeled-04",
                    "random-unlabeled-05",
                    "random-unlabeled-06",
                    "random-unlabeled-07"]
    _data_nagoya = ["2017_nagoya/" + e for e in _data_nagoya]

    _data_bitbotslab = ["ball_random_01"]
    _data_bitbotslab = ["2018_bitbotslab/" + e for e in _data_bitbotslab]

    DATA = _data_tuple(NAGOYA=_data_nagoya,
                       BITBOTSLAB=_data_bitbotslab,
                       ALL=[e for e in chain(_data_nagoya, _data_bitbotslab)])
