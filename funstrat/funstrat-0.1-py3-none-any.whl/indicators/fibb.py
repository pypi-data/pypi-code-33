from copy import deepcopy

import crayons as cy
import numpy as np
import skfuzzy as fuzz
import talib as ta
from copy import deepcopy
import pandas as pd


from funstrat.indicators.interface import Indicator
from funstrat.helpers.math import best_fit
from funstrat.helpers.array import col_filter
from funstrat.helpers import IndicatorBlock

from funhouse import TA, index_time
import skfuzzy.control as ctrl
from crayons import magenta, blue, green, cyan, red, yellow


def fib_row(current_row):
    if current_row['up6'] < current_row['price']:
        return 7
    elif current_row['up5'] <= current_row['price'] <= current_row['up6']:
        return 6
    elif current_row['up4'] <= current_row['price'] <= current_row['up5']:
        return 5
    elif current_row['up3'] <= current_row['price'] <= current_row['up4']:
        return 4
    elif current_row['up2'] <= current_row['price'] <= current_row['up3']:
        return 3
    elif current_row['up1'] <= current_row['price'] <= current_row['up2']:
        return 2
    elif current_row['basis'] <= current_row['price'] <= current_row['up1']:
        return 1
        
    elif current_row['low1'] <= current_row['price'] <= current_row['basis']:
        return -1
    elif current_row['low2'] <= current_row['price'] <= current_row['low1']:
        return -2
    elif current_row['low3'] <= current_row['price'] <= current_row['low2']:
        return -3
    elif current_row['low4'] <= current_row['price'] <= current_row['low3']:
        return -4
    elif current_row['low5'] <= current_row['price'] <= current_row['low4']:
        return -5
    elif current_row['low6'] <= current_row['price'] <= current_row['low5']:
        return -6
    elif current_row['price'] < current_row['low6']:
        return -7
    else:
        return 0

def fib_strength(local_fib):
    strength = 0
    if local_fib['fib_action'] == "BUY":
        if local_fib['position'] == -1:
            strength = 0.1
        if local_fib['position'] == -2:
            strength = 0.2
        if local_fib['position'] == -3:
            strength = 0.3
        if local_fib['position'] == -4:
            strength = 0.5
        if local_fib['position'] == -5:
            strength = 0.7
        if local_fib['position'] == -6:
            strength = 0.9
        if local_fib['position'] == -7:
            strength = 1.0


        if local_fib['position'] == 4:
            strength = 0.3
        if local_fib['position'] == 5:
            strength = 0.2
        if local_fib['position'] == 6:
            strength = 0.1
        if local_fib['position'] == 7:
            strength = 0
    if local_fib['fib_action'] == "SELL":
        if local_fib['position'] == 1:
            strength = 0.1
        if local_fib['position'] == 2:
            strength = 0.2
        if local_fib['position'] == 3:
            strength = 0.3
        if local_fib['position'] == 4:
            strength = 0.5
        if local_fib['position'] == 5:
            strength = 0.7
        if local_fib['position'] == 6:
            strength = 0.9
        if local_fib['position'] == 7:
            strength = 1.0
        

        if local_fib['position'] == -1:
            strength = 0.9
        if local_fib['position'] == -2:
            strength = 0.7
        if local_fib['position'] == -3:
            strength = 0.5
        if local_fib['position'] == -4:
            strength = 0.3
        if local_fib['position'] == -5:
            strength = 0.2
        if local_fib['position'] == -6:
            strength = 0.1
        if local_fib['position'] == -7:
            strength = 0
    return strength


class FIBBBIndicator(IndicatorBlock):
    def __init__(self, **kwargs):
        super().__init__()
        self.params = {
            "window": 14,
            "top": 50,
            "bottom": 35,
            "fuzzy_distro": "exp",
            # The regression observation windows (use to determine the change of the rsi)
            "regress": 5
        }
        
        self.ta = None
        self.trend = 'neutral'
        self.processed_fib = None
        # Add a pandas variable here
        self.fuzzy_level = 0.0
        self.set_ta_params(**kwargs)
        
        
        # m = ctrl.Consequent(universe, 'output')
        

    def update_fuzzy(self):
        self.params["top_fibb"] = np.linspace(self.params["top"], 101, 25)
        self.params["bottom_uni"] = np.linspace(0, self.params["bottom"], 25)

        # 


    
    def pre_fuzzy_process(self, rsi):
        """
            Get the derivative of the last 5 numbers,

        """
        # x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
        r = self.params['regress']
        x = rsi[:-r]
        bf = best_fit(x)
        # b2 = best_fit(x2)

        # (3.772040916256247, -5.220047202554735, 1.0, 0.0, 0.0)

        
        m = bf[0]
        b = bf[1]
        return m, b

    
    def _process_fuzzy(self, fibb_position, ftype):
        """ Set the fuzzy logic. Should return a number between 0 and 100. The number indicates the strength of a movement from the baseline."""
        # # TODO: LEARN HOW TO CREATE STEPS HERE
        # # TODO: LEARN HOW TO CREATE STEPS BASED ON A GIVEN DISTRIBUTION
        # # s = self.pre_fuzzy_process(rsi)

        # antnames = ["1", "2", "3", "4", "5", "6", "7"]
        # slope = ctrl.Antecedent(np.linspace(0, 4, 25), 'slope')
        # intercept = ctrl.Antecedent(np.linspace(20, 80, 25), 'intercept')
        # output = ctrl.Consequent(np.linspace(0, 100, 25), 'output')

        # rsi_ant = None

        # if ftype == "bottom":
        #     rsi_ant = np.linspace(self.params["top"], 101, 25)
        #     # Reverse the rules here

        # elif ftype == "top":
        #     rsi_ant = np.linspace(self.params["top"], 101, 25)
        # else:
        #     return

        # rsia = ctrl.Antecedent(rsi_ant, 'rsi')
        # slope.automf(names=antnames) 
        # # intercept.automf(names=antnames)
        # rsia.automf(names=antnames)
        # output.automf(names=antnames)


        # rsi1 = rsi[-1]
        # sabs = abs(s[0])
        
        # # Put together two different rule sets for top and bottom. Will proably be the norm for all indicators.
        # # if sim 
        # if self.trend == "positive":
        #     # Usually (-3, 7]
        #     rule1 = ctrl.Rule(antecedent=(rsia['1']), consequent=output['1'])
        #     rule2 = ctrl.Rule(antecedent=(rsia['2']), consequent=output['2'])
        #     rule3 = ctrl.Rule(antecedent=(rsia['3']), consequent=output['3'])
            
        #     rule4 = ctrl.Rule(antecedent=(rsia['4']), consequent=output['4'])
            
        #     rule5 = ctrl.Rule(antecedent=(rsia['5']), consequent=output['5'])
        #     rule6 = ctrl.Rule(antecedent=(rsia['6']), consequent=output['6'])
        #     rule7 = ctrl.Rule(antecedent=(rsia['7']), consequent=output['7'])
        
        #     system = ctrl.ControlSystem(rules=[rule1, rule2, rule3, rule4, rule5, rule6, rule7])
        #     # sim = ctrl.ControlSystemSimulation(system, flush_after_run=21 * 21 + 1)
        # elif self.trend == "negative":
        #     # Usually [-7, 3)
        #     rule1 = ctrl.Rule(antecedent=(rsia['1']), consequent=output['7'])
        #     rule2 = ctrl.Rule(antecedent=(rsia['2']), consequent=output['6'])
        #     rule3 = ctrl.Rule(antecedent=(rsia['3']), consequent=output['5'])
            
        #     rule4 = ctrl.Rule(antecedent=(rsia['4']), consequent=output['4'])
            
        #     rule5 = ctrl.Rule(antecedent=(rsia['5']), consequent=output['3'])
        #     rule6 = ctrl.Rule(antecedent=(rsia['6']), consequent=output['2'])
        #     rule7 = ctrl.Rule(antecedent=(rsia['7']), consequent=output['1'])
        # else:
        #     # Usually [-7, 7]
        #     pass
        # system = ctrl.ControlSystem(rules=[rule1, rule2, rule3, rule4, rule5, rule6, rule7])
        # sim = ctrl.ControlSystemSimulation(system, flush_after_run=21 * 21 + 1)
        
        # sim.input['rsi'] = rsi1
        # sim.compute()

        # self.fuzzy_level = sim.output['output']

    def set_ta_params(self, **kwargs):
        window = kwargs.get("window", None)
        top = kwargs.get("top", None)
        bottom = kwargs.get("bottom", None)
        regress = kwargs.get("regress", None)

        if window:
            self.params['window'] = window
        if top:
            self.params['top'] = top
        
        if bottom:
            self.params['bottom'] = bottom
        if regress:
            self.params['regress'] = regress

        self.update_fuzzy()
        return self
        

    def _run_ta(self):
        # print(self.df)
        current = TA(self.df).EMA(window=15).EMA(window=20).EMA(window=25).FIBBB(window=self.params['window'])
        return {
            "main": current.main,
            "fibb": current.fib
        }

    def _preprocess(self, next_ta):
        """ Preprocesses a all of the ta for the final decisions """
        # print("Preprocessing TA for decision logic")
        if next_ta is None:
            raise AttributeError("The TA library needs to be available")
        
        # Use np.select to put conditions on the exponential moving averages
        main_ta = next_ta['main']
        fibbb_ta = next_ta['fibb']
        
        main_cols = list(main_ta.columns)
        
        # print(main_cols)
        fcols = col_filter(main_cols, start="EMA")
        if len(fcols) != 3:
            raise ValueError("There should only be 3 columns")

        r = 5 # set using parameter optimization
        emcols = main_ta[fcols][:-r]

        t1 = best_fit(emcols[fcols[0]])
        t2 = best_fit(emcols[fcols[1]])
        t3 = best_fit(emcols[fcols[2]])

        if (t1[0] > 0.5) and (t2[0] > 0.5) and (t3[0] > 0.5):
            self.trend = 'positive'
        
        elif (t1[0] < -0.5) and (t2[0] < -0.5) and (t3[0] < -0.5):
            self.trend = 'negative'
        else:
            self.trend = "flat"

        fibbb_ta['position'] = fibbb_ta.apply(fib_row, axis=1)
        return fibbb_ta


    def calculate_position(self, preprocessed):
        if preprocessed is None:
            raise AttributeError("The processed fibonnaci data doesn't exist")
        
        local_fib = deepcopy(preprocessed)

        # print(cy.green("Current fibonacci", bold=True))
        # print(local_fib)

        local_fib['next-position'] = local_fib['position'].shift(1)
        local_fib = local_fib.dropna()
        


        local_fib['fib_action'] = np.where(local_fib['position'] > local_fib['next-position'], "SELL", "HOLD")
        local_fib['fib_action'] = np.where(local_fib['position'] < local_fib['next-position'], "BUY", local_fib['fib_action'])
        
            
        local_fib['fib_strength'] = local_fib.apply(fib_strength, axis=1)
        return local_fib[['fib_action', 'fib_strength', 'position']]


    def process(self, dataframe):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Should add dataframe")
        self.df = deepcopy(dataframe)
        self.df = self.df.sort_index()
        next_ta = self._run_ta()
        
        # next_ta
        preprocessed = self._preprocess(next_ta)

        final_position = self.calculate_position(preprocessed)

        result = final_position
        return result

# if __name__ == "__main__":
    # main()