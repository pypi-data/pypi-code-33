from setuptools import setup, find_packages

setup(
	name='rpi_d3m_primitives',  # This is the name of your PyPI-package.
	version='0.0.3',  # Update the version number for new releases
	author='Andrew Soszynski, Deniz Koyuncu, Zijun Cui, Qiang Ji',
	author_email='cuiz3@rpi.edu',
	url='https://www.ecse.rpi.edu/~cvrl/',
	description='RPI primitives for D3M submission.',
	platforms=['Linux', 'MacOS'],
        keywords = 'd3m_primitive',
	entry_points = {
		'd3m.primitives': [
			'feature_selection.simultaneous_markov_blanket.Auto_RPI = rpi_d3m_primitives.STMBplus_auto:STMBplus_auto',
            'feature_selection.adaptive_simultaneous_markov_blanket.Auto_RPI = rpi_d3m_primitives.aSTMBplus_auto:aSTMBplus_auto',
			'feature_selection.identity_parentchildren_markov_blanket.Auto_RPI = rpi_d3m_primitives.IPCMBplus_auto:IPCMBplus_auto',
			'feature_selection.joint_mutual_information.Auto_RPI = rpi_d3m_primitives.JMIplus_auto:JMIplus_auto',
			'feature_selection.simultaneous_markov_blanket.Manual_RPI = rpi_d3m_primitives.STMBplus:STMBplus',
            'feature_selection.adaptive_simultaneous_markov_blanket.Manual_RPI = rpi_d3m_primitives.aSTMBplus:aSTMBplus',
			'feature_selection.identity_parentchildren_markov_blanket.Manual_RPI = rpi_d3m_primitives.IPCMBplus:IPCMBplus',
			'feature_selection.joint_mutual_information.Manual_RPI = rpi_d3m_primitives.JMIplus:JMIplus',
			'feature_selection.score_based_markov_blanket.RPI = rpi_d3m_primitives.S2TMBplus:S2TMBplus',
			'classification.naive_bayes.RPI = rpi_d3m_primitives.NaiveBayes:NaiveBayes',
			'classification.tree_augmented_naive_bayes.RPI = rpi_d3m_primitives.TreeAugmentNB:TreeAugmentNB'
		],
	},
	install_requires=[
		'd3m'
	],
	packages=find_packages()
)
