import csv
from matplotlib import dates
import datetime as dt
import numpy as np
import pandas as pd
import sys
import matplotlib
matplotlib.use('TkAgg')
sys.path.insert(0, "../")
from interface_multi import c4gl_interface_soundings,get_record_yaml
from class4gl import class4gl_input, data_global,class4gl,units
#from sklearn.metrics import mean_squared_error
import matplotlib as mpl
import matplotlib.pyplot as plt
#import seaborn.apionly as sns
import pylab as pl
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kde
from scipy.stats import pearsonr                                                
from matplotlib import ticker
from interface_multi import c4gl_interface_soundings,get_record_yaml

c4gldata = {}

path_forcing = "/data/gent/vo/000/gvo00090/D2D/data/SOUNDINGS/GOAMAZON2/"
path_experiments = "/user/data/gent/gvo000/gvo00090/D2D/data/GOAMAZON/20190131/"
exp = 'BASE_ITER'

c4gldata[exp] = c4gl_interface_soundings( \
                  path_experiments+'/'+exp+'/',\
                  path_forcing+'/',\
                  None,\
                  refetch_records=False,
                  obs_filter = False,
                  tendencies_revised = False
                )

data = c4gldata[exp]

# select goamazon station
data.sel_station(STNID=90002)
# c4gldata[exp].next_record(-2)
obs_all = pd.read_csv('/user/data/gent/gvo000/gvo00090/EXT/archive/GOAMAZON/Pierre_AWS_Fluxos_2014_fluxes.csv')
obs_all["date"] = pd.Series([dt.datetime(2014,1,1)+dt.timedelta(seconds=((doy - 1.)*24.+4.)*3600.) for idoy,doy in obs_all.DOY.iteritems()])
obs_all["ldate"] = pd.Series([dt.datetime(2014,1,1)+dt.timedelta(seconds=((doy - 1.)*24.)*3600.) for idoy,doy in obs_all.DOY.iteritems()])

for idoy,doy in obs_all.DOY.iteritems():
    print(idoy,doy)

num_records = data.frames['profiles']['records_current_station_ini'].shape[0]



mod = []
obs = []
select = [1,2,3,4,5,6,7,13,14]
# select = range(num_records)
sel = 0

if (select[0]) > 0:
    data.next_record( (select[0]) - sel)

for j,i in enumerate(select):
    sel = i
    mod.append(pd.DataFrame())
    for var in ['H','LE']:
        temp = data.frames['profiles']['record_yaml_end_mod'].out.__dict__[var]
        temp = (temp[:-1] + temp[1:])/2.
        mod[-1][var] = temp

    #mod[-1] = pd.DataFrame(mod[-1][:-1]+ mod[-1][1:])[:-1]/2.
    
    mod[-1]['date'] = \
        [data.frames['profiles']['record_yaml_ini'].pars.datetime_daylight + \
         dt.timedelta(hours= time - \
                      data.frames['profiles']['record_yaml_end_mod'].out.time[0]) \
         for time in data.frames['profiles']['record_yaml_end_mod'].out.time[:-1]]
    mod[-1]['ldate'] = \
        [data.frames['profiles']['record_yaml_ini'].pars.ldatetime_daylight + \
         dt.timedelta(hours= time - \
                      data.frames['profiles']['record_yaml_end_mod'].out.time[0]) \
         for time in data.frames['profiles']['record_yaml_end_mod'].out.time[:-1]]
                        
    obs.append( pd.DataFrame(obs_all[\
                  (obs_all['date'] >= mod[-1]['date'][0]) & \
                  (obs_all['date'] <= mod[-1]['date'][-1])  \
                 ]))

    # ax.xaxis.set_major_locator(dates.HourLocator)
    if j+1 < len(select):
        data.next_record(select[j+1] - sel)


from matplotlib import pyplot as plt
fig = plt.figure(figsize=(7,7))
for j,i in enumerate(select):
    columns = 3
    
    ax = fig.add_subplot(np.ceil((len(select)/columns)),columns,j+1)
    ax.plot(obs[j].ldate,obs[j].H,'rx')
    ax.plot(mod[j].ldate,mod[j].H,'r-')
    ax.plot(obs[j].ldate,obs[j].LE,'gx')
    ax.plot(mod[j].ldate,mod[j].LE,'g-')
    ax.set_ylim((-100.,500.))
    ax.set_xlim((dt.datetime.combine(mod[j].ldate[0].date(),dt.time(hour=5)),
                dt.datetime.combine(mod[j].ldate[0].date(),dt.time(hour=19)))
                )
    xfmt = dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    plt.xticks( rotation= 70 )
    
    if j < len(select)-columns:
        ax.set_xticks([])
    if np.mod(j,columns) != 0:
        ax.set_yticks([])
    ax.set_title(mod[j].ldate[0].strftime("%Y/%m/%d"))

fig.subplots_adjust(top=0.95,bottom=0.1,left=0.1,right=0.977,hspace=0.215,wspace=0.15)
fig.show()

