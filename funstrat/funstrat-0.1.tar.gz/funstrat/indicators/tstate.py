import numpy as np
import skfuzzy as fuzz
import talib as ta
import pandas as pd

from funstrat.indicators.interface import Indicator
from funstrat.helpers.math import best_fit
from funstrat.helpers import IndicatorBlock
from funhouse import TA, index_time
import skfuzzy.control as ctrl
from crayons import cyan
from copy import deepcopy

# 10 ways for me to complete the prediction as quickly as possible:
# 1. Create a step number system (each step in a checkpoint can be referred to later)
# 2. Pull the stochastic data from before
# 3. Do normal step code to get everything working with existing portfolio
# 4. Use stochastic code every step of the process to super train network
# 5. Learn how to tabulate data in numpy using udemy tutorials
# 6. Create a reference number with the decision made
# 7. Add A config with the model server system
# 8. Quickly setup ray cluster to run LSTM model
# 9. Copy pasta Sam's code to get preprocessing done
# 10. Get all orders based on a UUID
# 11. Allow for a UUID to be entered into a portfolio server
# 12. Use all pandas features to preprocess
# 13. Take the template code from tutorial to handle preprocessing
# 14. pandas to_numpy
# 15. Pickle the state using the checkpointing library
# 16. Pickle the state, with the step it's currently in within both live and a given session
# 17. Get the reward after N number of steps
# 18. Crowdsource placing into production
# 19. Mix with portfolioenv class with N state


"""
# Outside array holds the rows, the columns are the inner arrays
[[1, 2, 3, 4, 5], []]
"""


"""
# Outside array holds the rows, the columns are the inner arrays
[[1, 2, 3, 4, 5], []]
"""


def fvol_strength(x):
    action = "NONE"
    vol_type = "NONE"
    vol = 0
    r1 = x["voltrans_rsi"]
    # if r1 > r2:
    if r1 < 43.0:
        vol_type = "INCREASE"
        vol = 0.1
    if r1 < 42.0:
        vol = 0.3
    if r1 < 38.0:
        vol = 0.4
    if r1 < 35.0:
        vol = 0.6
    if r1 < 30.0:
        vol = 0.7
    if r1 < 24.0:
        vol = 0.8
    if r1 < 20.0:
        vol = 0.9
    if r1 < 15.0:
        vol = 1
    # if r1 < r2:
    if r1 > 65.0:
        vol_type = "DECREASE"
        vol = 0.1
    if r1 > 67.0:
        vol = 0.3
    if r1 > 70.0:
        vol = 0.4
    if r1 > 80.0:
        vol = 0.6
    if r1 > 89.0:
        vol = 0.7
    if r1 > 92.0:
        vol = 0.8
    if r1 > 95.0:
        vol = 0.9
    if r1 > 97.0:
        vol = 1
        
    if vol > 0.3:
        action = "MOVE" 
    # x['stength'] = vol
    # x['taction'] = action
            # print(cyan(vol, bold=True))
    return vol


def fvol_type(x):
    action = 0 # "NONE"
    vol_type = 0 # "NONE"
    vol = 0
    r1 = x["voltrans_rsi"]
    # if r1 > r2:
    if r1 < 43.0:
        vol_type = 1 # "INCREASE"
        vol = 0.1
    if r1 < 42.0:
        vol = 0.3
    if r1 < 38.0:
        vol = 0.4
    if r1 < 35.0:
        vol = 0.6
    if r1 < 30.0:
        vol = 0.7
    if r1 < 24.0:
        vol = 0.8
    if r1 < 20.0:
        vol = 0.9
    if r1 < 15.0:
        vol = 1
    # if r1 < r2:
    if r1 > 65.0:
        vol_type = -1 #"DECREASE"
        vol = 0.1
    if r1 > 67.0:
        vol = 0.3
    if r1 > 70.0:
        vol = 0.4
    if r1 > 80.0:
        vol = 0.6
    if r1 > 89.0:
        vol = 0.7
    if r1 > 92.0:
        vol = 0.8
    if r1 > 95.0:
        vol = 0.9
    if r1 > 97.0:
        vol = 1

    if vol > 0.3:
        action = "MOVE"
    x['vol_type'] = vol_type
    x['stength'] = vol
    x['taction'] = action
    # print(cyan(vol, bold=True))
    return vol_type


def fvol_action(x):
    action =  0# "NONE"
    vol_type = "NONE"
    vol = 0
    r1 = x["voltrans_rsi"]
    # if r1 > r2:
    if r1 < 43.0:
        vol_type = "INCREASE"
        vol = 0.1
    if r1 < 42.0:
        vol = 0.3
    if r1 < 38.0:
        vol = 0.4
    if r1 < 35.0:
        vol = 0.6
    if r1 < 30.0:
        vol = 0.7
    if r1 < 24.0:
        vol = 0.8
    if r1 < 20.0:
        vol = 0.9
    if r1 < 15.0:
        vol = 1
    # if r1 < r2:
    if r1 > 65.0:
        vol_type = "DECREASE"
        vol = 0.1
    if r1 > 67.0:
        vol = 0.3
    if r1 > 70.0:
        vol = 0.4
    if r1 > 80.0:
        vol = 0.6
    if r1 > 89.0:
        vol = 0.7
    if r1 > 92.0:
        vol = 0.8
    if r1 > 95.0:
        vol = 0.9
    if r1 > 97.0:
        vol = 1

    if vol > 0.3:
        action = 1 # "MOVE"

    return action

class TransitionState(IndicatorBlock):
    """ 
        This is the transition state indicator. It's a mash up of many indicators to indicate various transition states.
        For example:
            - Bear/Bull/Flat indicator:
                - Uses three TEMA with different sizes to determine
            - RSI based volatility pridiction (using ATR, RSI (on ))

    """
    def __init__(self, **kwargs):
        super().__init__()
        self.params = {
            "e1": 20,
            "e2": 50, 
            "e3": 100,
            "window": 14
        }
        self.fuzzy_level = 0.0
        self.set_ta_params(**kwargs)
        
        
        # m = ctrl.Consequent(universe, 'output')
        

    def update_fuzzy(self):
        self.params["top_uni"] = np.linspace(self.params["top"], 101, 25)
        self.params["bottom_uni"] = np.linspace(0, self.params["bottom"], 25)

        # 



    def pre_fuzzy_process(self, rsi):
        """
            Get the derivative of the last 5 numbers,

        """
        r = self.params['regress']
        x = rsi[:-r]
        bf = best_fit(x)

        m = bf[0]
        b = bf[1]
        return m, b

    def fuzzy_logic(self, rsi, ftype):
        """ Set the fuzzy logic. Should return a number between 0 and 100. The number indicates the strength of a movement from the baseline."""
        # TODO: LEARN HOW TO CREATE STEPS HERE
        # TODO: LEARN HOW TO CREATE STEPS BASED ON A GIVEN DISTRIBUTION
        s = self.pre_fuzzy_process(rsi)

        antnames = ["weak", "mildly-weak", "mild", "mildly-strong", "strong"]
        slope = ctrl.Antecedent(np.linspace(0, 3.5, 25), 'slope')
        intercept = ctrl.Antecedent(np.linspace(20, 80, 25), 'intercept')
        output = ctrl.Consequent(np.linspace(0, 100, 25), 'output')

        rsi_ant = None

        if ftype == "bottom":
            rsi_ant = self.params["bottom_uni"]
            # Reverse the rules here

        elif ftype == "top":
            rsi_ant = self.params["top_uni"]
        else:
            return

        rsia = ctrl.Antecedent(rsi_ant, 'rsi')
        slope.automf(names=antnames) 
        # intercept.automf(names=antnames)
        rsia.automf(names=antnames)
        output.automf(names=antnames)


        rsi1 = rsi[-1]
        sabs = abs(s[0])
        
        # Put together two different rule sets for top and bottom. Will proably be the norm for all indicators.
        # if sim 
        if ftype == "top":
            rule0 = ctrl.Rule(antecedent=(rsia['weak']), consequent=output['weak'])
            rule1 = ctrl.Rule(antecedent=(rsia['mild']), consequent=output['mild'])
            rule2 = ctrl.Rule(antecedent=(rsia['strong']), consequent=output['strong'])
            rule3 = ctrl.Rule(antecedent=(rsia['mildly-weak']), consequent=output['mildly-weak'])
            rule4 = ctrl.Rule(antecedent=(rsia['mildly-strong']), consequent=output['strong'])
        
            system = ctrl.ControlSystem(rules=[rule0, rule1, rule2])
            # sim = ctrl.ControlSystemSimulation(system, flush_after_run=21 * 21 + 1)
        else:
            rule0 = ctrl.Rule(antecedent=(rsia['strong']), consequent=output['weak'])
            rule1 = ctrl.Rule(antecedent=(rsia['mild']), consequent=output['mild'])
            rule2 = ctrl.Rule(antecedent=(rsia['weak']), consequent=output['strong'])
            rule3 = ctrl.Rule(antecedent=(rsia['mildly-weak']), consequent=output['strong'])
            rule4 = ctrl.Rule(antecedent=(rsia['mildly-strong']), consequent=output['mildly-weak'])
        
            system = ctrl.ControlSystem(rules=[rule0, rule1, rule2, rule3, rule4])
        sim = ctrl.ControlSystemSimulation(system, flush_after_run=21 * 21 + 1)
        
        sim.input['rsi'] = rsi1
        sim.compute()

        self.fuzzy_level = sim.output['output']

        pass

    def set_ta_params(self, **kwargs):
        e1 = kwargs.get("e1")
        e2 = kwargs.get("e2")
        e3 = kwargs.get("e3")
        window = kwargs.get("window")

        if e1:
            self.params['e1'] = e1
        
        if e2:
            self.params['e2'] = e2
        
        if e3:
            self.params['e3'] = e3
        
        if window:
            self.params["window"] = window
        

        return self
        
    
    def _run_ta(self):
        # TODO: Upgrade TA library for JIT acceleration. Will speed for better training use
        self.ta = TA(self.df).VolTrans(window=self.params['window']).main


    def process(self, dataframe):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Should add dataframe")
        self.df = deepcopy(dataframe)
        self._run_ta()

        self.ta['voltrans_rsi_change'] = self.ta['voltrans_rsi'].shift(1)
        self.ta = self.ta.dropna()
        self.ta['vol_type'] = self.ta.apply(fvol_type, axis=1)
        self.ta['stength'] = self.ta.apply(fvol_strength, axis=1)
        self.ta['taction'] = self.ta.apply(fvol_action, axis=1)
        self.ta = self.ta.drop(columns=['voltrans_rsi_change'])
        return self.ta
