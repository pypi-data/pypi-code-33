# -*- coding: utf-8 -*-

import xarray as xr
import pandas as pd
import io
import os
import numpy as np
import datetime as dt
import Pysolar
import sys
import pytz
import glob
sys.path.insert(0,'/user/home/gent/vsc422/vsc42247/software/class4gl/class4gl/')
from class4gl import class4gl_input, data_global,class4gl
from interface_multi import stations,stations_iterator, records_iterator,get_record_yaml,get_records


def esat(T):
    return 0.611e3 * np.exp(17.2694 * (T - 273.16) / (T - 35.86))
def efrom_rh100_T(rh100,T):
    return esat(T)*rh100/100.
Rd         = 287.                  # gas constant for dry air [J kg-1 K-1]
cp         = 1005.                 # specific heat of dry air [J kg-1 K-1]
Rv         = 461.5                 # gas constant for moist air [J kg-1 K-1]
epsilon = Rd/Rv # or mv/md
def qfrom_e_p(e,p):
    return epsilon * e/(p - (1.-epsilon)*e)


def humppa_parser(balloon_file,file_sounding,ldate,lhour,c4gli=None):
        print(balloon_file)
        
        xrin = balloon_file
        air_balloon = pd.DataFrame()

        air_balloon['t'] = xrin.tdry.values+273.15
        air_balloon['p'] = xrin.pres.values*100.
        
        air_balloon['u'] = xrin.u_wind.values
        air_balloon['v'] = xrin.v_wind.values
        air_balloon['WSPD'] = xrin['wspd'].values
        
        print(xrin.rh.values.shape)
        air_balloon['q'] = qfrom_e_p(efrom_rh100_T(xrin.rh.values,air_balloon['t'].values),air_balloon.p.values)
        

        #balloon_conv = replace_iter(balloon_file,"°","deg")
        #readlines = [ str(line).replace('°','deg') for line in balloon_file.readlines()]
        #air_balloon = pd.read_fwf( io.StringIO(''.join(readlines)),skiprows=8,skipfooter=15)
        # air_balloon_in = pd.read_fwf(balloon_file,
        #                              widths=[14]*19,
        #                              skiprows=9,
        #                              skipfooter=15,
        #                              decimal=',',
        #                              header=None,
        #                              names = columns,
        #                              na_values='-----')
    

        
        rowmatches = {
            'R' :    lambda x: (Rd*(1.-x.q) + Rv*x.q),
            'theta': lambda x: (x['t']) * (x['p'][0]/x['p'])**(x['R']/cp),
            'thetav': lambda x: x.theta  + 0.61 * x.theta * x.q,
            'rho': lambda x: x.p /x.t / x.R ,
        }
        for varname,lfunction in rowmatches.items():
            air_balloon[varname] = lfunction(air_balloon)
        
        print('alt in xrin?:','alt' in xrin)
        if 'alt' in xrin:
            air_balloon['z'] = xrin.alt.values
        else:
            air_balloon['z'] = 0.
            for irow,row in air_balloon.iloc[1:].iterrows():
                air_balloon['z'].iloc[irow] = air_balloon['z'].iloc[irow-1] - \
                        2./(air_balloon['rho'].iloc[irow-1]+air_balloon['rho'].iloc[irow]) * \
                        (air_balloon['p'].iloc[irow] - air_balloon['p'].iloc[irow-1])
                        
             
        for varname,lfunction in rowmatches.items():
            air_balloon[varname] = lfunction(air_balloon)
        
        dpars = {}
        dpars['longitude']  = current_station['longitude']
        dpars['latitude']  = current_station['latitude'] 
        
        dpars['STNID'] = current_station.name
        

        # # there are issues with the lower measurements in the HUMPPA campaign,
        # # for which a steady decrease of potential temperature is found, which
        # # is unrealistic.  Here I filter them away
        # ifirst = 0
        # while  (air_balloon.theta.iloc[ifirst+1] < air_balloon.theta.iloc[ifirst]):
        #     ifirst = ifirst+1
        # print ('ifirst:',ifirst)
        # air_balloon = air_balloon.iloc[ifirst:].reset_index().drop(['index'],axis=1)
        air_balloon = air_balloon.iloc[:].reset_index().drop(['index'],axis=1)
        
        is_valid = ~np.isnan(air_balloon).any(axis=1) & (air_balloon.z >= 0)
        valid_indices = air_balloon.index[is_valid].values
        
        air_ap_mode='b'
        
        if len(valid_indices) > 0:
            print(air_balloon.z.shape,air_balloon.thetav.shape,)
            dpars['h'],dpars['h_u'],dpars['h_l'] =\
                blh(air_balloon.z,air_balloon.thetav,air_balloon.WSPD)
            dpars['h_b'] = np.max((dpars['h'],10.))
            dpars['h_u'] = np.max((dpars['h_u'],10.)) #upper limit of mixed layer height
            dpars['h_l'] = np.max((dpars['h_l'],10.)) #low limit of mixed layer height
            dpars['h_e'] = np.abs( dpars['h_u'] - dpars['h_l']) # error of mixed-layer height
            dpars['h'] = np.round(dpars['h_'+air_ap_mode],1)
        else:
            dpars['h_u'] =np.nan
            dpars['h_l'] =np.nan
            dpars['h_e'] =np.nan
            dpars['h'] =np.nan
        
        
        
        if ~np.isnan(dpars['h']):
            dpars['Ps'] = air_balloon.p.iloc[valid_indices[0]]
        else:
            dpars['Ps'] = np.nan
        
        if ~np.isnan(dpars['h']):
        
            # determine mixed-layer properties (moisture, potential temperature...) from profile
            
            # ... and those of the mixed layer
            is_valid_below_h = is_valid & (air_balloon.z < dpars['h'])
            valid_indices_below_h =  air_balloon.index[is_valid_below_h].values
            if len(valid_indices) > 1:
                if len(valid_indices_below_h) >= 3.:
                    ml_mean = air_balloon[is_valid_below_h].mean()
                else:
                    ml_mean = air_balloon.iloc[valid_indices[0]:valid_indices[1]].mean()
            elif len(valid_indices) == 1:
                ml_mean = (air_balloon.iloc[0:1]).mean()
            else:
                temp =  pd.DataFrame(air_balloon)
                temp.iloc[0] = np.nan
                ml_mean = temp
                       
            dpars['theta']= ml_mean.theta
            dpars['q']    = ml_mean.q
            dpars['u']    = ml_mean.u
            dpars['v']    = ml_mean.v 
        else:
            dpars['theta'] = np.nan
            dpars['q'] = np.nan
            dpars['u'] = np.nan
            dpars['v'] = np.nan
        
        air_ap_head = air_balloon[0:0] #pd.DataFrame(columns = air_balloon.columns)
        # All other  data points above the mixed-layer fit
        air_ap_tail = air_balloon[air_balloon.z > dpars['h']]



        air_ap_head.z = pd.Series(np.array([2.,dpars['h'],dpars['h']]))
        jump = air_ap_head.iloc[0] * np.nan
        
        if air_ap_tail.shape[0] > 1:
        
            # we originally used THTA, but that has another definition than the
            # variable theta that we need which should be the temperature that
            # one would have if brought to surface (NOT reference) pressure.
            for column in ['theta','q','u','v']:
               
               # initialize the profile head with the mixed-layer values
               air_ap_head[column] = ml_mean[column]
               # calculate jump values at mixed-layer height, which will be
               # added to the third datapoint of the profile head
               jump[column] = (air_ap_tail[column].iloc[1]\
                               -\
                               air_ap_tail[column].iloc[0])\
                              /\
                              (air_ap_tail.z.iloc[1]\
                               - air_ap_tail.z.iloc[0])\
                              *\
                              (dpars['h']- air_ap_tail.z.iloc[0])\
                              +\
                              air_ap_tail[column].iloc[0]\
                              -\
                              ml_mean[column] 
               if column == 'theta':
                  # for potential temperature, we need to set a lower limit to
                  # avoid the model to crash
                  jump.theta = np.max((0.1,jump.theta))
        
               air_ap_head[column][2] += jump[column]
        
        air_ap_head.WSPD = np.sqrt(air_ap_head.u**2 +air_ap_head.v**2)



        # only select samples monotonically increasing with height
        air_ap_tail_orig = pd.DataFrame(air_ap_tail)
        air_ap_tail = pd.DataFrame()
        print(air_ap_tail_orig)
        air_ap_tail = air_ap_tail.append(air_ap_tail_orig.iloc[0],ignore_index=True)
        for ibottom in range(1,len(air_ap_tail_orig)):
            if air_ap_tail_orig.iloc[ibottom].z > air_ap_tail.iloc[-1].z +10.:
                air_ap_tail = air_ap_tail.append(air_ap_tail_orig.iloc[ibottom],ignore_index=True)


        # make theta increase strong enough to avoid numerical
        # instability
        air_ap_tail_orig = pd.DataFrame(air_ap_tail)
        # air_ap_tail = pd.DataFrame()
        # #air_ap_tail = air_ap_tail.append(air_ap_tail_orig.iloc[0],ignore_index=True)
        # air_ap_tail = air_ap_tail.append(air_ap_tail_orig.iloc[0],ignore_index=True)
        # theta_low = air_ap_head['theta'].iloc[2]
        # z_low = air_ap_head['z'].iloc[2]
        # ibottom = 0
        # for itop in range(0,len(air_ap_tail_orig)):
        #     theta_mean = air_ap_tail_orig.theta.iloc[ibottom:(itop+1)].mean()
        #     z_mean =     air_ap_tail_orig.z.iloc[ibottom:(itop+1)].mean()
        #     if (
        #         #(z_mean > z_low) and \
        #         (z_mean > (z_low+10.)) and \
        #         #(theta_mean > (theta_low+0.2) ) and \
        #         #(theta_mean > (theta_low+0.2) ) and \
        #          (((theta_mean - theta_low)/(z_mean - z_low)) > 0.00001)):

        #         air_ap_tail = air_ap_tail.append(air_ap_tail_orig.iloc[ibottom:(itop+1)].mean(),ignore_index=True)
        #         ibottom = itop+1
        #         theta_low = air_ap_tail.theta.iloc[-1]
        #         z_low =     air_ap_tail.z.iloc[-1]
        #     # elif  (itop > len(air_ap_tail_orig)-10):
        #     #     air_ap_tail = air_ap_tail.append(air_ap_tail_orig.iloc[itop],ignore_index=True)
        # 
        air_ap = \
            pd.concat((air_ap_head,air_ap_tail)).reset_index().drop(['index'],axis=1)
        
        # we copy the pressure at ground level from balloon sounding. The
        # pressure at mixed-layer height will be determined internally by class
        
        rho        = 1.2                   # density of air [kg m-3]
        g          = 9.81                  # gravity acceleration [m s-2]
        
        air_ap['p'].iloc[0] =dpars['Ps'] 
        air_ap['p'].iloc[1] =(dpars['Ps'] - rho * g * dpars['h'])
        air_ap['p'].iloc[2] =(dpars['Ps'] - rho * g * dpars['h'] -0.1)
        
        
        dpars['lat'] = dpars['latitude']
        # this is set to zero because we use local (sun) time as input (as if we were in Greenwhich)
        dpars['lon'] = 0.
        # this is the real longitude that will be used to extract ground data
        
        dpars['ldatetime'] = ldate+dt.timedelta(hours=lhour)
        dpars['datetime'] =  dpars['ldatetime'] + dt.timedelta(hours=-4)
        dpars['doy'] = dpars['datetime'].timetuple().tm_yday
        
        dpars['SolarAltitude'] = \
                                Pysolar.GetAltitude(\
                                    dpars['latitude'],\
                                    dpars['longitude'],\
                                    dpars['datetime']\
                                )
        dpars['SolarAzimuth'] =  Pysolar.GetAzimuth(\
                                    dpars['latitude'],\
                                    dpars['longitude'],\
                                    dpars['datetime']\
                                )
        
        
        dpars['lSunrise'], dpars['lSunset'] \
        =  Pysolar.util.GetSunriseSunset(dpars['latitude'],
                                         0.,
                                         dpars['ldatetime'],0.)
        
        # Warning!!! Unfortunatly!!!! WORKAROUND!!!! Even though we actually write local solar time, we need to assign the timezone to UTC (which is WRONG!!!). Otherwise ruby cannot understand it (it always converts tolocal computer time :( ). 
        dpars['lSunrise'] = pytz.utc.localize(dpars['lSunrise'])
        dpars['lSunset'] = pytz.utc.localize(dpars['lSunset'])
        
        # This is the nearest datetime when the sun is up (for class)
        dpars['ldatetime_daylight'] = \
                                np.min(\
                                    (np.max(\
                                        (dpars['ldatetime'],\
                                         dpars['lSunrise'])\
                                     ),\
                                     dpars['lSunset']\
                                    )\
                                )
        # apply the same time shift for UTC datetime
        dpars['datetime_daylight'] = dpars['datetime'] \
                                    +\
                                    (dpars['ldatetime_daylight']\
                                     -\
                                     dpars['ldatetime'])
        
        
        # We set the starting time to the local sun time, since the model 
        # thinks we are always at the meridian (lon=0). This way the solar
        # radiation is calculated correctly.
        dpars['tstart'] = dpars['ldatetime_daylight'].hour \
                         + \
                         dpars['ldatetime_daylight'].minute/60.\
                         + \
                         dpars['ldatetime_daylight'].second/3600.
        
        dpars['sw_lit'] = False
        # convert numpy types to native python data types. This provides
        # cleaner data IO with yaml:
        for key,value in dpars.items():
            if type(value).__module__ == 'numpy':
                dpars[key] = dpars[key].item()
        
                decimals = {'p':0,'t':2,'theta':4, 'z':2, 'q':5, 'u':4, 'v':4}
        # 
                for column,decimal in decimals.items():
                    air_balloon[column] = air_balloon[column].round(decimal)
                    air_ap[column] = air_ap[column].round(decimal)
        
        updateglobal = False
        if c4gli is None:
            c4gli = class4gl_input()
            updateglobal = True
        
        print('updating...')
        print(column)
        c4gli.update(source='humppa',\
                    # pars=pars,
                    pars=dpars,\
                    air_balloon=air_balloon,\
                    air_ap=air_ap)
        if updateglobal:
            c4gli.get_global_input(globaldata)

        # if profile_ini:
        #     c4gli.runtime = 10 * 3600

        c4gli.dump(file_sounding)
        
        # if profile_ini:
        #     c4gl = class4gl(c4gli)
        #     c4gl.run()
        #     c4gl.dump(file_model,\
        #               include_input=True,\
        #               timeseries_only=timeseries_only)
        #     
        #     # This will cash the observations and model tables per station for
        #     # the interface
        # 
        # if profile_ini:
        #     profile_ini=False
        # else:
        #     profile_ini=True
        return c4gli
