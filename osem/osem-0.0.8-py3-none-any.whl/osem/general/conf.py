# this is the configuration file for OSEM
import os
import json

############################################################
# default variables for all the modules
# data_folder = "data"
dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
data_folder = os.path.join(dir_path, 'osem/general/data')
cutoff = 0.45  # used to compare string, 1 is a perfect match on the string, with 0 all string match.

##############################################################
# default variables for the acesss data feature

# kbob
version_default = '2016'
data_folder_kbob = os.path.join(data_folder, 'data_kbob')
basename_unit = "kbob_unit"  # filename for the unit file: basename + version +'.csv'
basename_kbob = "kbob_data"  # filename for the kbob file: basename + version +'.csv'
filename_trans_ind = "kbob_translation_indicator.csv"   # name of the file with the translation data
ref_kbob = "Friedli R., Gugerli H. «Plattform «Ökobilanzdaten im Baubereich» Gründungsdokument, Coordination Group " \
           "for Construction and Property Service (KBOB).» 2011"

# political objectives
basename_pol = "political_obj.csv"
column_not_print_pol = ['reference_year', 'objective_year', 'note', 'reference']  # columns which are not objectives

# price
precision_price = 5  # to which precision the price in CHF must be calculated
basename_price = "price_database.db"
name_tableunit = 'UNIT_TECHNO'
column_not_print_price = ["units", "reference", "note"]  # columns which are not a type of price
ref_col = "reference"
myind = "myind"
nb_point_graph = 50
interp_lim = 0.3
warning_ignore = '.*Covariance of the parameters could not be estimated.*'
opex_name = 'maintenance'

# kpi
temp_building = [[50, 25, 25], [70, 60, 50]]  # # [[%percent building], [temperature]]
filename_eff = 'kpi_efficiency_heating.csv'
temp_ext = 22  # exterior temperature °C
kpi_from_price = ['CAPEX', 'OPEX']

# meteo data
data_folder_meteo = os.path.join(data_folder, 'data_meteo_swiss')
filenames = [i for i in os.listdir(data_folder_meteo) if i != 'data_source.txt']
nbline_header = 5  # the number of lines which compsed the header (no empty line)
line_with_unit = 6  # the index of the line where the unit is (with empty line)
col_name = ['station_name', 'elev_m', 'coordinates_CH', 'period_reference', 'january', 'february', 'march', 'april',
            'may', 'june','july', 'august', 'september', 'october', 'november', 'december', 'annual']
month_name = ['january', 'february', 'march', 'april', 'may', 'june','july', 'august', 'september', 'october',
              'november', 'december']


###############################################################
# default value for the plot

# plot kpi
xlabel = 'Years'
ylabelco2 = 'CO$_{2}$ emission [kg]'
ylabelfinal = 'Final Energy [kWh]'
ylabelprimary = 'Primary Energy [kWh]'
ylabelrenew = 'Primary Energy [kWh]'
renew_colname = ['years', 'scenarios','renewable', 'non-renewable']
fontsize =12
width = 0.2
figsize = (8,8)


#############################################################
# default value for network

# pandangas

default_levels = {"HP": 5.0E5, "MP": 1.0E5, "BP+": 0.1E5, "BP": 0.025E5}  # Pa
lhv = 38.1E3  # kJ/kg
v_max = 2.0  # m/s
temperature = 10 + 273.15  # K
p_atm = 101325
scaling = 1
min_p_pa = 0.022E5
mat_default = 'steel'
corr_pnom = 1 # the ratio between the max pressure (p_nom) and the average pressure of the network

default_solver_option= {'tol_mat_mass': 1e-10,
                        'tol_mat_pres': 1e-10,
                        'maxiter': 1e7,
                        'gtol': 1e-5,
                        'round_num': 5,
                        'disp' : False,
                        'min_residual': 3,
                        'iter_print': 50
}

filename_info_solver = 'pandangas_info_solver_option.json'

########################################################################
#reference

ref_girardin = "L.Girardin, A GIS-based Methodology for the Evaluation of Integrated Energy Systems in Urban Area, " \
               "PhD thesis, EPFL, Lausanne, 2012"

ref_static_heating_cooling_power = "D. Perez. A framework to model and simulate the disaggregated energy flows " \
                                   "supplying buildings in urban areas . PhD thesis, LESO-PB EPFL, Lausanne, 2014 and " \
                                   "Catalogue des ponts thermiques, OFEN "

ref_energy_requirement = "Novatlantis, Steps towards a sustainable development, a White Book for R&D of energy-efficient " \
                         "technologies, February 2004 and " + ref_girardin

ref_maximum_legal_heating_demand = "SIA 380/1 Norm, heating thermal energy in buildings, edition 2009"

ref_heat_network = "C. Weber. Multi-Objective Design and Optimization of District Energy Systems Including " \
                   "Polygeneration Energy Conversion Technologies, PhD thesis, Lausanne, 2008"

ref_heat_exchanger = "F.P. Incropera and D.P. DeWitt, 1990, Fundamentals of Heat and Mass Tranfert, 3rd edition, " \
                     "pp. 658-660, Wiley, New York"

ref_solar_pv = " EMD international A/S, Solar Collectors and Photovolotaic in energyPro, 2013 and A. Luque " \
               "and S. Hegedus, Eds., Handbook of photovoltaic science and engineering. Hoboken, NJ: Wiley, 2003."

ref_thermal_solar_pv = "Fischer, W. Heidemann, H. Muller-Steinhagen, B. Perers, P. Bergquist, and B. Hellstrom, " \
                       "Collector test method under quasi-dynamic conditions according to the European " \
                       "Standard EN 12975-2 Solar Energy, vol. 76, no. 1-3, pp. 117-123, Jan. 2004 and " \
                       "SPF, Institut Fur SolarTechnik, Collectors, http://www.spf.ch/index.php?id=111&L=6&no_cache=1"

ref_geothermal = "Agence Qualite Construction. Maugard, Alain. Pompes a chaleur geothermiques - Les operations de" \
                 " forage et limite de prestations. Paris, France. Programme d'action pour la qualite de la" \
                 " construction et la transition energetique. 2014-07."

ref_solar_function_incident_angle = "Duffie,J.A. and Beckman W.A. Solar Engineering of Thermal Processes (4th edition), " \
                                    "chapter 1.6 and B. Perers, P. Kovacs, M. Olsson, and M. P. U. Pettersson, " \
                                    "A Tool for Standardized Collector Performance Calculations including PVT" \
                                    " Energy Procedia, vol. 30, pp. 1354-1364, 2012."

ref_solar_function_onto_tilted_plane = "B. Perers, P. Kovacs, M. Olsson, and M. P. U. Pettersson, A Tool for " \
                                       "Standardized Collector Performance Calculations including PVT Energy Procedia," \
                                       " vol. 30, pp. 1354-1364, 2012."

ref_hot_water_tank =  "Rejane De Cesaro Oliveski, Arno Krenzinger, Horacio A. Vielmo, Comparison between models for the" \
                      " simulation of hot water storage tanks, Solar Energy, Volume 75, Issue 2, August 2003, " \
                      "Pages 121-134"

ref_statified_dyn = " I. Dincer, M. Rosen: Thermal Energy Storage : Systems and Applications, Wiley and Sons Inc, 2002, " \
                    "pp. 276 - 287 and W.A. Beckman, J.A. Duffie: Solar Engineering of Thermal Processes, second " \
                    "edition, Wiley and Sons Inc, 1991, pp. 379-384"


#############################
data_folder_enerapi = os.path.join(data_folder, 'enerapi_data')
file_per = 'period_RegBL.json'
file_affect = 'affect_RegBL.json'
file_ratio = 'ratio_base.json'
file_sia_380_1 ='data_SIA_380-1.json'
file_em_system ='em_system.json'

file_project_nature = 'Data_Project_Nature.json'
file_boiler_techno = 'boiler_techno.json'
file_construct_bat = 'Construct_Bat.json'
file_data_qhli ='Data_Qhli.json'
file_meteo_2028 ='Meteo2028.json'
file_sse_coef_orient ='SSE_Coef_Orient.json'
file_window_ratio ='WindowRatio.json'
file_window_type_incident_rate ='WindowTypeIncidentRate.json'




year_period = [1,1919,1946,1961,1971,1981,1986,1991,1996,2001,2006,2011,2015]