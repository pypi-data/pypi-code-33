import load
import datetime

start_date = datetime.datetime(2018, 1, 1)
end_date = datetime.datetime(2018, 5, 1)

ticker = "btcusd"
timeframe = 1440

data = load.import_data(ticker, timeframe, start_date, end_date)
print(data)
print(data['open'])
