from datetime import datetime
from tradingene.data.load import import_data
from tradingene.algorithm_backtest.tng import TNG
import tradingene.backtest_statistics.backtest_statistics as bs

START_DATE = datetime(2018, 1, 1)  # The first day of simulated trading period
END_DATE = datetime(2018, 2, 1)  # The last day of simulated trading period
TICKER = "btcusd"  # A ticker to use
TIMEFRAME = 60  # A timeframe to use

_short_position = None  # To save ids of short positions opened throughout backtest.
_long_position = None  # To save ids of short positions opened throughout backtest.


def onShortPositionClose(
):  # This function is called when a short position is being closed
    global _short_position
    _short_position = None  # Resetting since no opened position exists now...


def onLongPositionClose(
):  # This function is called when a long position is being closed
    global _long_position
    _long_position = None  # Resetting since no opened position exists now...


def onBar(instrument):
    global _short_position, _long_position

    bollinger10 = instrument.bollinger(
        10)  # Retrieving the value of the Bollinger indicator of period 10.
    atr10 = instrument.atr(
        10)  # Retrieving the value of the ATR indicator of period 10.
    if instrument.close[1] > bollinger10.top[1]:  # If the price rises above the Bollinger top line...
        if _long_position is None:  # ... and if there is no opened long position yet...
            _long_position = _alg.openLong(1)  # ...buying 1 lot.
            if _long_position is not None:
                _alg.setSLTP(
                    loss=atr10[1] * 2,
                    profit=atr10[1] * 2)  # Setting stop loss and take profit
                _alg.onPositionClose(
                    _long_position, onLongPositionClose
                )  # Specifying the function to be called when the position is being closed
    elif instrument.close[1] < bollinger10.bottom[1]:  # If the price falls below the Bollinger bottom line...
        if _short_position is None:  # ... and if there is no opened short position yet...
            _short_position = _alg.openShort(1)  # ... selling 1 lot.
            if _short_position is not None:
                _alg.setSLTP(
                    loss=atr10[1] * 2,
                    profit=atr10[1] * 2)  # Setting stop loss and take profit
                _alg.onPositionClose(
                    _short_position, onShortPositionClose
                )  # Specifying the function to be called when the position is being closed


_alg = TNG(
    START_DATE, END_DATE
)  # Creating an instance of the class (TNG) to run the algorithm within.
_alg.addInstrument(TICKER)  # Adding an instrument.
_alg.addTimeframe(TICKER, TIMEFRAME)  # Adding a time frame.
_alg.run_backtest(onBar)  # Backtesting...

stat = bs.BacktestStatistics(_alg)  # Retrieving statistics of the backtest

pnl = stat.calculate_PnL()
num_positions = stat.calculate_number_of_trades()
print("pnl=%f, num_positions=%d" % (pnl, num_positions))

stat.backtest_results()  # Displaying the backtest statistics
