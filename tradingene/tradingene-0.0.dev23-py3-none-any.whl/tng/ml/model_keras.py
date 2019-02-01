import numpy as np

import dill as dill
import keras
from load import import_data
import datetime
from prepare_data import prepare_data


def main():
    print("Loading rates...")
    #rates = load("BTCUSD_D.csv", startYear=2015, endYear=2018)
    start_date = datetime.datetime(2018, 1, 1)
    end_date = datetime.datetime(2018, 5, 1)
    rates = import_data("btcusd", 1440, start_date, end_date)
    print("Read %d 'candle bars' from %s to %s" % (len(
        rates['close']), str(rates['time'][-1]), str(rates['time'][0])))
    # Parameters to calculate inputs and outputs
    params = {
        'look_back_period': 100,
        'look_back_rate': 10,
        'look_ahead_period': 10,
        'look_ahead_price_change': 1.17
    }
    print("Preparing data...")
    # Preparing data, i.e. calculating inputs and outputs
    data_for_model = prepare_data(rates, calc_inp, calc_out, params)
    if data_for_model is None:
        print("Failed to prepare data.\nExiting...")
        return
    print("Prepared.")
    data_x = data_for_model['inputs']
    data_y = keras.utils.np_utils.to_categorical(data_for_model['labels'], 3)
    #data_y = data_for_model['labels']

    input_vectors_num, input_vector_size = np.shape(data_x)
    model = keras.models.Sequential()
    model.add(
        keras.layers.Dense(
            input_vectors_num // 2,
            activation="sigmoid",
            input_shape=(input_vector_size, )))  #я Input layer
    # Next go hidden layer(s)
    model.add(keras.layers.Dense(input_vectors_num // 2, activation="sigmoid"))
    # At last goes the output one
    model.add(keras.layers.Dense(3, activation='sigmoid'))
    model.compile(
        optimizer="sgd", loss="categorical_crossentropy", metrics=["accuracy"])
    model.fit(
        data_x,
        data_y,
        epochs=10,
        batch_size=input_vectors_num // 10,
        shuffle=True)
    (loss, accuracy) = model.evaluate(data_x, data_y)
    print("FIT EVALUATION: loss={:.4f}, accuracy= {:.4f}%".format(
        loss, accuracy * 100))
    save_model("keras.md", model, calc_inp, params)
    print("The model has been saved into the 'keras.md' file.")


# end of main


def calc_inp(rates, params):
    inp = []
    look_back_period = params['look_back_period']
    look_back_rate = params['look_back_rate']
    higher_highs_num = 0
    lower_lows_num = 0
    len_rates = len(rates['close'])
    if look_back_period < len_rates:
        for i in range(1, look_back_period + 1):
            if rates['high'][i - 1] > rates['high'][i]:
                higher_highs_num += 1
            if rates['low'][i - i] < rates['low'][i]:
                lower_lows_num += 1
            if i > 0 and i % look_back_rate == 0:
                overall_num = higher_highs_num + lower_lows_num
                if overall_num > 0:
                    inp.append(higher_highs_num / overall_num)
                    inp.append(lower_lows_num / overall_num)
                else:
                    inp.append(0.0)
                    inp.append(0.0)
    if len(inp) == 0:
        return None
    return inp


# end of def


def calc_out(rates, params):
    ret_val = 1, 0
    look_ahead_period = params['look_ahead_period']
    look_ahead_price_change = params['look_ahead_price_change']
    len_rates = len(rates['close'])
    if len_rates < look_ahead_period:
        stop_look_at = len_rates
    else:
        stop_look_at = look_ahead_period
    for i in range(stop_look_at):
        if not (rates['high'][i] / rates['open'][0] < look_ahead_price_change):
            ret_val = 2, look_ahead_price_change
            break
        if not (rates['open'][0] / rates['low'][i] < look_ahead_price_change):
            ret_val = 0, -look_ahead_price_change
            break
    return ret_val


# end of def


def save_model(file_name, model, calc_inp, params):
    # with open(file_name, 'wb') as file_handle:
    # 	dill.dump({"model": model, "calc_inp": calc_inp, "params":params}, file_handle)
    ok = True
    try:
        file_handle = open(file_name, 'wb')
    except Exception:
        ok = False
    if ok:
        try:
            dill.dump({
                "model": model,
                "calc_inp": calc_inp,
                "params": params
            }, file_handle)
        except Exception:
            ok = False
        finally:
            file_handle.close()
    return True


def load_model(file_name):
    # with open(file_name, 'rb') as file_handle:
    # 	loaded = dill.load(file_handle)
    ok = True
    try:
        file_handle = open(file_name, 'rb')
    except Exception:
        ok = False
    if ok:
        try:
            loaded = dill.load(file_handle)
        except Exception:
            ok = False
        finally:
            file_handle.close()
    if not ok:
        return None
    return {
        'model': loaded['model'],
        'calc_inp': loaded['calc_inp'],
        'params': loaded['params']
    }


# end of loadModel()

main()
