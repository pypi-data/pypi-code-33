import pandas as pd

def load_weather():
    return pd.read_pickle('weather.pckl')
