# These are the names of the modules, and the functions of the modules we want to execute

default_conf = {

	'Time': {
		# Has to exist, must be string
		'class': 'ts_featurizer.tools.featurizers.TimeFeaturizer',

		# Optional, if exists has to be dict
		'previous_trans': {},

		# Features has to exist, must be dict
		# Each key must be a str(that can be converted to callable), and the item must be a list (of dicts)
		# Each dict of that list can only have three keys (max), named 'send_all_data', 'args' and 'kwargs'
		# send_all_data must be a boolean
		# args must be a list
		# kwargs must be a dictionary

		'features': {
			'numpy.mean': [],
			'numpy.median': [],
			'numpy.std': [],
			'numpy.min': [],
			'numpy.max': [],
			'scipy.stats.kurtosis': [],
			'scipy.stats.sem': [],
			'scipy.stats.skew': [],
			'numpy.percentile': [
				{'args': [50], },
				{'args': [95], 'kwargs': {}}
			],
			'ts_featurizer.tools.signal_energy': [],
		},
		# Optional, if exists, dict

	},

	'Frequency': {
		'class': 'ts_featurizer.tools.featurizers.FrequencyFeaturizer',

		'previous_trans': {
			'ts_featurizer.tools.to_frequency': {'args': [], 'kwargs': {}}
		},
		'features': {
			'ts_featurizer.tools.detect_peaks': [
				{'kwargs': {'show': False, }, 'test': {
					'preprocessors': {
						'ts_featurizer.tools.get_list_from_columns': {}  # Keyword arguments
					},  # TODO OrderedDict??
				}, 'model': {'preprocessor': 'ts_featurizer.tools.get_most_important_freqs', 'kwargs': {}}}

			],
			'ts_featurizer.tools.signal_energy': [{}],

		},

	},

	# 'Hilbert': {
	# 	'class': 'ts_featurizer.tools.featurizers.HilbertFeaturizer',
	#
	# 	'previous_trans': {
	# 		'ts_featurizer.tools.to_hilberts_freq': {'args': [], 'kwargs': {}}
	# 	},
	# 	'features': {
	# 		'ts_featurizer.tools.detect_peaks': [
	# 			{'kwargs': {'show': False, }, 'fill_gaps': True, 'test': {
	# 				'preprocessors': {
	# 					'ts_featurizer.tools.get_list_from_columns': {}  # Keyword arguments
	# 				},  # TODO OrderedDict??
	# 			}}
	#
	# 		],
	# 		'ts_featurizer.tools.signal_energy': [{}],
	#
	# 	},
	#
	# },
	# 'AR': {
	# 	'class': 'ts_featurizer.tools.featurizers.AutoRegressionFeaturizer',
	# 	'previous_trans': {},
	# 	'features': {
	#
	# 		'ts_featurizer.tools.get_AR_params': [
	# 			{'test': {
	# 				'preprocessors': {
	# 					'ts_featurizer.tools.get_one_from_col': {
	#
	# 						'col': 'best_order'
	#
	# 					}  # Keyword arguments
	# 				},  # TODO OrderedDict?? Azken finian aurreprozesaketa egiterako orduan inportantia da ordena
	# 			},
	# 				'model': {'preprocessor': 'ts_featurizer.tools.get_AR_model', 'kwargs': {'max_coeffs': 3, }}
	#
	# 			},
	#
	# 		],
	#
	# 	},
	# },

	# 'Wavelet': {
	# 	'class': 'ts_featurizer.tools.featurizers.WaveletFeaturizer',
	# 	'previous_trans': {},
	# 	'features': {
	# 		'ts_featurizer.tools.wavelet_transform': [
	# 			{'args': [], 'kwargs': {'wavelet': 'db2'}}
	# 		]
	#
	# 	},
	# },

}
