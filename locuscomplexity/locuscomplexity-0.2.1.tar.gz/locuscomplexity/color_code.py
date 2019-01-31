import os
import pickle

dirname, filename = os.path.split(os.path.abspath(__file__))

# Build the dict_color pickle file from activity_colors and resource_colors
# That can be downloaded here (first and second page):
# https://docs.google.com/spreadsheets/d/1Z-vv12vjxiqpHq8wztIDdYw3-CyfGjt9tq_LzmLlktY/edit#gid=0

# def dict_colors():
#     activities = pd.read_csv(os.path.join(dirname,'../data/external/activity_colors.csv'))
#     resources = pd.read_csv(os.path.join(dirname,'../data/external/resource_colors.csv'))
#     act36 = activities.set_index('36 Activities').to_dict()['HEX']
#     act12 = activities[['12 Activities','HEX']].dropna()
#     act12 = act12.set_index('12 Activities').to_dict()['HEX']
#     act4 = activities[['4 Activities','HEX']].dropna()
#     act4 = act4.set_index('4 Activities').to_dict()['HEX']
#     act36.update(act12)
#     act36.update(act4)
#     res = resources.set_index('Resource').to_dict()['Hex']
#     res.update(act36)
#     return res

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_data(path):
    return os.path.join(_ROOT, path)


RES_COLORS = {'A': '4095cb', 'A1': '89c7ed', 'A2': '6eb7e4', 'A3': '57a5d6', 'A4': '4095cb',
 'B': '36a092', 'B1': '72c8bd', 'B2': '59baad', 'B3': '46aca2', 'B4': '36a092',
 'C': 'f2cd54', 'C1': 'ffe1a5', 'C2': 'fad889', 'C3': 'f6d26f', 'C4': 'f2cd54',
 'D': 'e75f2d', 'D1': 'fc9f59', 'D2': 'f58c4a', 'D3': 'ec733c', 'D4': 'e75f2d',
 'E': 'd23131', 'E1': 'f76e5e', 'E2': 'eb584d', 'E3': 'de433e', 'E4': 'd23131',
 'F': '746b98', 'Div': '#616261', '1.1.1': 'a62481', '1.1.2': 'c3277c',
 '1.1.3': 'cd235e', '1.2.1': 'd8223f', '1.2.2': 'e22220', '1.2.3': 'e43720',
 '1.3.1': 'e74c1f', '1.3.2': 'e9611e', '1.3.3': 'eb701d', '2.1.1': 'ee7e1d',
 '2.1.2': 'f08d1f', '2.1.3': 'f4a022', '2.2.1': 'f8b225', '2.2.2': 'fcc528',
 '2.2.3': 'f9cf2a', '2.3.1': 'f6da2b', '2.3.2': 'f3e42d', '2.3.3': 'd0d628',
 '3.1.1': 'aec824', '3.1.2': '8bba25', '3.1.3': '5dab37', '3.2.1': '2d9c48',
 '3.2.2': '018d5a', '3.2.3': '06907a', '3.3.1': '0c929a', '3.3.2': '1395ba',
 '3.3.3': '1389b6', '4.1.1': '1d7cb3', '4.1.2': '296faf', '4.1.3': '3264a7',
 '4.2.1': '3a59a0', '4.2.2': '434d98', '4.2.3': '514693', '4.3.1': '5e3f8f',
 '4.3.2': '6c388a', '4.3.3': '892685', 1.1: 'a62481', 1.2: 'd8223f', 1.3: 'e74c1f',
 2.1: 'ee7e1d', 2.2: 'f8b225', 2.3: 'f6da2b', 3.1: 'aec824', 3.2: '2d9c48',
 3.3: '0c929a', 4.1: '1d7cb3', 4.2: '3a59a0', 4.3: '5e3f8f', 1.0: 'a62481',
 2.0: 'ee7e1d', 3.0: 'aec824', 4.0: '1d7cb3'}


LIGHT_GRAY = '#eae8e6'
MID_GRAY = '#c6c6c7'
BLUE_GRAY = '#a0aabf'



def color(locus_code):

    try:
        locus_code = locus_code.split(' ')[0]
        if locus_code in RES_COLORS:
            if RES_COLORS[locus_code].startswith('#'):
                return RES_COLORS[locus_code]
            return '#' + RES_COLORS[locus_code]
        else:
            for code in RES_COLORS:
                if locus_code.startswith(code) or code.startswith(locus_code):
                    if RES_COLORS[code].startswith('#'):
                        return RES_COLORS[code]
                    return '#' + RES_COLORS[code]
    except:
        print('error')
        return BLUE_GRAY
