from enum import Enum


class ClockExogType(Enum):
    all = 'all'
    deep = 'deep'
    single = 'single'
    slide = 'slide'


class Clock:
    def __init__(self,
                 endog_data,
                 endog_names,
                 exog_data,
                 exog_names,
                 metrics_dict,
                 train_size,
                 test_size,
                 exog_num,
                 exog_num_comb,
                 num_bootstrap_runs
                 ):
        self.endog_data = endog_data
        self.endog_names = endog_names
        self.exog_data = exog_data
        self.exog_names = exog_names
        self.metrics_dict = metrics_dict
        self.train_size = train_size
        self.test_size = test_size
        self.exog_num = exog_num
        self.exog_num_comb = exog_num_comb
        self.num_bootstrap_runs = num_bootstrap_runs
