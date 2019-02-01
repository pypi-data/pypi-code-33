# Compatibility
from __future__ import division, print_function

# Third party libraries
import os
import json
import warnings
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime as dt

# Local imports/HRV toolbox imports
import pyhrv
import pyhrv.tools as tools


def time_varying(nni=None, rpeaks=None, parameter=None, func=None, duration=300, show=True):
	# Check input
	nn = tools.check_input(nni, rpeaks)

	# Check if parameter is not on the list of invalid parameters (e.g. avoid plot functions)
	invalid_parameters = ['plot', 'tinn_m', 'tinn_n', 'fft_nfft', 'fft_window', 'fft_resampling_frequency',
						  'fft_interpolation', 'ar_nfft', 'ar_order', 'lomb_nfft', 'lomb_ma']
	for p in invalid_parameters:
		if p in parameter:
			raise ValueError("Invalid parameter '%s'. This parameter is not supported by this function." % parameter)

	# Load HRV parameters (hrv_keys.json) metadata & check if the parameter is a pyHRV parameter
	params = json.load(open(os.path.join(os.path.split(__file__)[0], './files/hrv_keys.json'), 'r'), encoding='utf-8')
	if parameter not in params.keys():
		raise ValueError("Invalid parameter '%s'. This parameter seems to be unknown to pyHRV." % parameter)

	# Get function name for the requested parameter
	func = params[parameter][-1]
	unit = params[parameter][2]

	# Get segments of NNI data
	segments, worked = tools.segmentation(nni, duration=duration, full=True)

	# If segmentation worked, i.e. NNI series duration > segment duration
	if worked:
		output_values = []
		# Compute parameter for each segment
		for segment in segments:
			try:
				# Try to pass the show and mode argument to to suppress PSD plots
				val = eval(func + '(nni=segment, mode=\'dev\')[0][\'%s\']' % parameter)
			except TypeError as e:
				if 'mode' in str(e):
					try:
						# If functions has now mode feature but 'mode' argument, but a plotting feature
						val = eval(func + '(nni=segment, plot=False)[\'%s\']' % parameter)
					except TypeError as a:
						if 'plot' in str(a):
							# If functions has now plotting feature try regular function
							val = eval(func + '(nni=segment)[\'%s\']' % parameter)
						else:
							raise TypeError(e)

			# Collect parameter value
			output_values.append(val)

		# Create matplotlib figure
		fig = plt.figure()
		ax = fig.add_subplot(111)

		# Prepare time vector
		duration = int(duration / 60.)
		t_vector = range(0, len(output_values) * duration, duration)

		# Plot
		ax.plot(t_vector, output_values)

		# X-Axis configuration
		# Set x-axis format to seconds if the duration of the signal <= 60s
		nni_duration = int(float(np.sum(nni) / 1000.))
		if nni_duration <= 60:
			ax.set_xlabel('Time [s]')
		# Set x-axis format to MM:SS if the duration of the signal > 60s and <= 1h
		elif 60 < nni_duration <= 3600:
			ax.set_xlabel('Time [MM:SS]')
			formatter = mpl.ticker.FuncFormatter(lambda ms, x: str(dt.timedelta(seconds=ms))[2:])
			ax.xaxis.set_major_formatter(formatter)
		# Set x-axis format to HH:MM:SS if the duration of the signal > 1h
		else:
			ax.set_xlabel('Time [HH:MM:SS]')
			formatter = mpl.ticker.FuncFormatter(lambda ms, x: str(dt.timedelta(seconds=ms)))
			ax.xaxis.set_major_formatter(formatter)

		ax.set_xticks(t_vector, minor=True)
		ax.xaxis.grid(which='minor', color='b', lw=0.7, alpha=0.5, linestyle='--')
		ax.axis([0, t_vector[-1], np.min(output_values) * 0.6, np.max(output_values) * 1.2])
		ax.set_ylabel('%s [$%s$]' % (parameter.upper(), unit))
		ax.set_title('Time Varying Evolution of %s' % parameter.upper())
		ax.legend([mpl.patches.Patch(facecolor='b', alpha=0.0)],
				  ['Segment Duration: %i [min]' % duration])

		# Show
		if show:
			plt.show()

nni=np.load('../TestData/segments_long/series_38.npy')
nni = np.append(nni, nni)

time_varying(nni, parameter="fft_ratio", duration=300)
