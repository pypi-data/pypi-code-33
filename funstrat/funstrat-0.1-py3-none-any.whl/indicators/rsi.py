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


def apply_sim(row, sim):
    pass


def set_top_bottom(row, top, bottom):
    if row['rsi'] < bottom:
        return "bottom"
    elif row['rsi'] > top:
        return "top"
    return "none"


def set_action(row):
    if row['classification'] == "bottom":
        return "BUY"
    elif row['classification'] == "top":
        return "SELL"
    return "HOLD"

def set_fuzzy(row, _ts, rsii):

    a = _ts.fuzzy_logic(rsii, row['classification'], row['rsi'])
    # print(a)
    return a
    
    

class RSIIndicator(IndicatorBlock):
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
        self.fuzzy_level = 0.0
        self.set_ta_params(**kwargs)
        
        
        # m = ctrl.Consequent(universe, 'output')
        

    def update_fuzzy(self):
        self.params["top_uni"] = np.linspace(self.params["top"], 101, 25)
        self.params["bottom_uni"] = np.linspace(0, self.params["bottom"], 25)

    



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

    def suck(self):
        print("DICK")

    def fuzzy_logic(self, rsi, ftype, current_price):
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


        rsi1 = current_price
        # print(current_price)
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
        sim = ctrl.ControlSystemSimulation(system)
        # print(sim)
        
        sim.input['rsi'] = rsi1
        sim.compute()

        return sim.output['output']
        # return sim

        # First rule
        # This should have an output of strong buys
        # rule0 = ctrl.Rule(antecedent=((slope['weak'] & intercept['mild'] & rsia['strong']) |
        #                       (slope['strong'] & intercept['strong'] & rsia['mild']) |
        #                       (slope['strong'] & intercept['mild'] & rsia['mild'])),
        #           consequent=output['nb'], label='rule nb')
        
        # # This rule should have an output of mediocre buys
        # rule1 = ctrl.Rule(antecedent=((error['nb'] & delta['ze']) |
        #                             (error['nb'] & delta['ps']) |
        #                             (error['ns'] & delta['ns']) |
        #                             (error['ns'] & delta['ze']) |
        #                             (error['ze'] & delta['ns']) |
        #                             (error['ze'] & delta['nb']) |
        #                             (error['ps'] & delta['nb'])),
        #                 consequent=output['ns'], label='rule ns')

        # # This rule set should have an output of weak buys
        # rule2 = ctrl.Rule(antecedent=((error['nb'] & delta['pb']) |
        #                             (error['ns'] & delta['ps']) |
        #                             (error['ze'] & delta['ze']) |
        #                             (error['ps'] & delta['ns']) |
        #                             (error['pb'] & delta['nb'])),
        #                 consequent=output['ze'], label='rule ze')

        pass

    def set_ta_params(self, **kwargs):
        window = kwargs.get("window")
        top = kwargs.get("top")
        bottom = kwargs.get("bottom")
        regress = kwargs.get("regress")

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
        # TODO: Upgrade TA library for JIT acceleration. Will speed for better training use
        self.ta = TA(self.df).RSI(window=self.params['window']).main


    def process(self, dataframe):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Should add dataframe")
        self.df = deepcopy(dataframe)
        self._run_ta()
        
        # Serious manual coding goes here to make a decision with expected output
        rsii = self.ta["RSI_{}".format(self.params['window'])]
        self.rsii = rsii
        rsiii = pd.DataFrame()
        rsiii['rsi'] = rsii
        # print(rsii[-4])
        # Run an apply to have all rows
        # rsii
        rsiii['classification'] = rsiii.apply((lambda x: set_top_bottom(x, self.params["top"], self.params["bottom"])), axis=1)
        rsiii['rsi_action'] = rsiii.apply(set_action, axis=1)
        rsiii['fuzzy'] = rsiii.apply((lambda x: set_fuzzy(x, self, rsii)), axis=1).fillna(0)
        # rsiii.fillna(0)
        # print(rsiii)
        # if rsii[-1] < self.params['bottom']:
        #     # Input bottom, top, 
        #     self.fuzzy_logic(rsii, "bottom")
        #     return "BUY", self.fuzzy_level, rsii[-1]
        # elif rsii[-1] > self.params['top']:
        #     self.fuzzy_logic(rsii, "top")
        #     return "SELL", self.fuzzy_level, rsii[-1]
        # return "HOLD", self.fuzzy_level, rsii[-1]
        return rsiii
# def main():
#     close = numpy.random.beta(1, 100, size=10000) * 1000
#     # print()
#     output = ta.RSI(close)
#     # print(output)
#     for i in output:
#         if i > 50:
#             print("Sell")
#         elif i < 45:
#             print("BUY")
#         else:
#             print(i)


# if __name__ == "__main__":
    # main()