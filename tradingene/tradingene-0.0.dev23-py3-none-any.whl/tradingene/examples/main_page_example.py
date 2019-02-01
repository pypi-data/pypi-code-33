from datetime import datetime
from tradingene.algorithm_backtest.tng import TNG
from tradingene.backtest_statistics import backtest_statistics as bs

name = "Cornucopia"
regime = "SP"
start_date = datetime(2018, 9, 1)
end_date = datetime(2018, 10, 1)
alg = TNG(name, regime, start_date, end_date)
alg.addInstrument("btcusd")
alg.addTimeframe("btcusd", 1440)


def onBar(instrument):
    if instrument.open[1] > instrument.close[1]:
        # If the price moved down we take a short position
        alg.sell()
    elif instrument.open[1] < instrument.close[1]:
        # If the price moved up we take a long position
        alg.buy()
    else:
        # If the price did not change then do nothing
        pass


alg.run_backtest(onBar)
stats = bs.BacktestStatistics(alg)
stats.backtest_results(plot=True, filename="backtest_stats")
