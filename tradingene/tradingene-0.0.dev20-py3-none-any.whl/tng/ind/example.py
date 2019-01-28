import tng.algorithm_backtest.tng as tng
from datetime import datetime
import tng.backtest_statistics.backtest_statistics as bs
import pandas as pd

name = "Cornucopia"
regime = "SP"
start_date = datetime(2018, 4, 29, 21, 00)
end_date = datetime(2018, 5, 1)

alg = tng.TNG(name, regime, start_date, end_date)
alg.addInstrument("btcusd")
alg.addTimeframe("btcusd", 30)


def onBar(instrument):
    print(instrument.time)
    print("ad = ", instrument.ad()[1])
    print("adx = ", instrument.adx(4, 4).adx[1])
    print("apo = ", instrument.apo(13, 26)[1])
    print("aroon = ", instrument.aroon(5).up[1])
    print("atr = ", instrument.atr(3)[1])
    print("bollinger = ", instrument.bollinger(8).top[1])
    print("cci = ", instrument.cci(7)[1])
    print("chande = ", instrument.chande(5)[1])
    print("ema = ", instrument.ema(3)[1])
    print("keltner = ", instrument.keltner(4).basis[1])
    print("macd = ", instrument.macd(2, 3, 3).macd[1])
    print("momentum = ", instrument.momentum(7)[1])
    print("ppo = ", instrument.ppo(13, 26)[1])
    print("roc = ", instrument.roc(7)[1])
    print("rsi = ", instrument.rsi(4)[1])
    print("sma = ", instrument.sma(7)[1])
    print("stochastic = ", instrument.stochastic(7, 3).k[1])
    print("trima = ", instrument.trima(6)[1])
    print("williams = ", instrument.williams(14)[1])
    print("======================================")
    # if instrument.open[1] > instrument.close[1]:
    #     # If price goes down during the day then sell;
    #     alg.sell()
    # elif instrument.open[1] < instrument.close[1]:
    #     # If price goes up during the day then buy;
    #     alg.buy()
    # else:
    #     # If price did not change then do nothing;
    #     pass


alg.run_backtest(onBar)
# df.to_csv("btcusd30.csv", index = False, header = False)
# new_stat = bs.BacktestStatistics(alg.positions)
# new_stat.backtest_results()
#new_stat.calculate_ATT()
# new_stat.print_statistics()
# print(new_stat.calculate_drawdown())
# print(new_stat.calculate_PnL())
# print(new_stat.calculate_AT())
# print(new_stat.calculate_profit())
# print(new_stat.calculate_loss())
# print(new_stat.calculate_AWT())
# print(new_stat.calculate_ALT())
# print(new_stat.calculate_LWT())
# print(new_stat.calculate_LLT())
# print(new_stat.calculate_MCW())
# print(new_stat.calculate_MCL())
