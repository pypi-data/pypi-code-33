import pandas as pd
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn
seaborn.set(palette='deep',style='darkgrid')
import QUANTAXIS as QA

def SQ_denoise_get_z_shape(df, threshold_z=5, split_point=None,points_list = ['09:25:00','15:00:00']):
    '''
    data为单列dataframe输入，为fac列
    '''
    data = df.copy()
    data = data.fillna(method='ffill')
    fac = data.columns.tolist()[0]
    data['minute'] = list(map(lambda x: (str(x)), data.index))
    data['point'] = np.nan
    data[fac + '_z'] = np.nan
    data['count'] = np.arange(0, len(data))

    '''
    每天开盘和收盘和隔离点的位置要定点，信息量比较大
    '''
    for ii in points_list:
        data['point'] = np.where(data['minute'] == ii, 0, data['point'])
    # data['point'] = np.where(data['minute'] == '09:25:00', 0, data['point'])
    # data['point'] = np.where(data['minute']=='09:30:00',0,data['point'])
    # data['point'] = np.where(data['minute']=='11:29:00',0,data['point'])
    # data['point'] = np.where(data['minute']=='11:30:00',0,data['point'])
    # data['point'] = np.where(data['minute']=='13:00:00',0,data['point'])
    # data['point'] = np.where(data['minute'] == '15:00:00', 0, data['point'])
    if split_point == None: pass
    else:
        data['point'] = np.where(data['minute'] == split_point, 0, data['point'])

    data[fac + '_z'] = np.where(data['point'] == 0, data[fac], np.nan)

    for i in range(data.shape[0]):
        print(i)
        if i <= 0:
            fac_record = data[fac].iloc[i]
            place_record = i
            place_change_record = i
            continue
        else:
            pass

        '''
        重要变量：
        temp_point
        fac_temp
        data_max
        data_min

        gap_max_temp
        gap_min_temp
        gap_max_record
        gap_min_record

        fac_record
        place_record
        '''
        temp_point = data['point'].iloc[i]
        fac_temp = data[fac].iloc[i]
        data_window = (data[[fac]].iloc[place_record + 1:i + 1])

        data_max = data_window.max()[0]
        data_min = data_window.min()[0]
        gap_max_record = abs(data_max - fac_record)
        gap_min_record = abs(data_min - fac_record)
        gap_max_temp = abs(data_max - fac_temp)
        gap_min_temp = abs(data_min - fac_temp)

        if (gap_max_record > gap_min_record) & (gap_max_temp >= threshold_z):
            update = 'max'
        elif (gap_max_record < gap_min_record) & (gap_min_temp >= threshold_z):
            update = 'min'
        else:
            update = None

        if update == 'max':
            print('gap: ' + str(gap_max_temp))
            time_max = data_window[data_window[fac] == data_max].index[-1]
            data['point'][data.index == time_max] = 1
            fac_record = data[data.index == time_max][fac][0]
            place_record = data[data.index == time_max]['count'][0]
            place_change_record = i

        if update == 'min':
            print('gap: ' + str(gap_min_temp))
            time_min = data_window[data_window[fac] == data_min].index[-1]
            data['point'][data.index == time_min] = -1
            fac_record = data[data.index == time_min][fac][0]
            place_record = data[data.index == time_min]['count'][0]
            place_change_record = i

        if temp_point == 0:
            fac_record = data[fac].iloc[i]
            place_record = i
            place_change_record = i

    data[fac + '_z'] = np.where((data['point'] == 0) | (data['point'] == 1) | (data['point'] == -1), data[fac],
                                np.nan)
    data[fac + '_z'][0] = data[fac][0]
    data['steps'] = np.arange(0, len(data))
    data_z = data[(data['point'] == 0) | (data['point'] == 1) | (data['point'] == -1)]
    data_z[fac + '_z_delta'] = data_z[fac + '_z'].shift(-1) - data_z[fac + '_z']
    data_z['steps_delta'] = data_z['steps'].shift(-1) - data_z['steps']
    data_z['add_fac'] = data_z[fac + '_z_delta'] / data_z['steps_delta']
    data['add_fac'] = data_z['add_fac']
    data['add_fac'] = data['add_fac'].fillna(method='ffill')
    data['cum_add_fac'] = data['add_fac'].cumsum()
    data['z_result'] = data[fac + '_z'][0] + data['cum_add_fac'].shift(1)
    data['z_result'][0] = data[fac + '_z'][0]
    data[fac+'_z'] = data['z_result']
    data[fac + '_z_point'] = data['point']
    return data[[fac+'_z', 'point']]



