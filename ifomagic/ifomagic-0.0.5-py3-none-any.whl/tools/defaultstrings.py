'''
File containing strings to use when communicating with the user.

MAGIC
@author: Isobel
'''

# Instructions
instruction = {}
instruction['make_changes'] = '''
	Make changes to the detector? (y/n)
	'''
instruction['changes_or_additions'] = '''
	Would you like to change the detector's parameters?
	Or would you like to add your own?
	To see a list of variable parameters, press 'p'.
	To add or change one that you already know, press 'y'.
	Press any other key to continue without changing anything.
	'''
instruction['enter_param_name'] = '''
	Please enter the parameter name, then press enter.
	'''
instruction['enter_param_val'] = '''
	Please enter the new value of this parameter.
	To enter a single numeric value, enter a single number.
	To enter a list, first enter 'l'.
	To enter a boolean value, preceed your entry with the letter 'B'.
	'''
instruction['enter_list'] = '''
	Enter your list as single numbers separated by spaces.
	'''
instruction['add_or_change_or_continue'] = '''
	Press 'y' to add or change another parameter, or press 
	any other key to continue.
	'''
instruction['first_mass'] = '''
Please enter the first mass (in units of solar mass):
	'''
instruction['second_mass'] = '''
Please enter the second mass (in units of solar mass):
'''

# Flags
flag = {}
flag['boolean_entry'] = 'MAGIC things your value is a Boolean.'
flag['invalid_boolean'] = 'Invalid boolean'
flag['list_entry'] = 'MAGIC things your value is a list.'
flag['invalid_list'] = 'Invalid list'
flag['single_number'] = 'MAGIC thinks your entry is a single number.'
flag['invalid_number'] = 'Invalid number'
flag['final_plot'] = 'Final plot being shown'

flag['inspiral_estimate'] = '''
	We are going to estimate how many binary mergers your detector can see, 
	based on the inspiral signal!
	'''
flag['imr_estimate'] = '''
	We are going to estimate how many binary mergers your detector can see!
	'''


def flagInterfacing(ifo_name=''):
    return 'Interfacing to interferometer ' + ifo_name + '...'


def flagBestSensitivity(best_s, best_f):
    return '''
	Best sensitivity of {s:.3E} Hz^(-1/2) achieved at
	a frequency of {f:.3f} Hz.
	'''.format(
        s=best_s, f=best_f)


def flagRange(m1, m2, D):
    return '''
	Your detector can see binary mergers of masses {M1:.1f} M_sol and {M2:.1f} M_sol to 
	a distance of {dist:.2f} Mpc.
	'''.format(
        M1=m1, M2=m2, dist=D)


def flagPath(path):
    return 'Noise data written to file ' + path


def flagOldParameter(name, value):
    return 'Old parameter : ' + str(name) + ' = ' + str(value)


def flagNewParameter(name, value):
    return 'New parameter : ' + str(name) + ' = ' + str(value)
