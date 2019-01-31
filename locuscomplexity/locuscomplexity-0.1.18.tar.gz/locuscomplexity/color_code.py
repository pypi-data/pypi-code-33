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

with open(get_data('data/dict_colors.pkl'), 'rb') as colors:
    RES_COLORS = pickle.load(colors)

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
