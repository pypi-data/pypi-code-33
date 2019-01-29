import os
import pyjags
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

class ModelHandler:
	"""A class for defining the parameters used to generate a PyJAGS model.

	PyJAGS is a Python module designed to provide an interface to the JAGS
	Gibbs sampling application. This class contains methods for processing
	a simple string that specifies a model into a format PyJAGS will accept.

	For usage, print attributes `specification_template` and `model_template`.

	Attributes:
		specification_template: a demonstration of how to specify model properties
		model_template: a demonstration of how to define a JAGS model.
		model: a string representing the JAGS model to be passed to PyJAGS
	"""

	def __init__(self, spec:str) -> None:
		"""Read in model specification string and store values to pass to PyJAGS"""
		self.configure(spec)
		self.modelfile= self.modelfile.rstrip()
		if self.modelfile.endswith('.txt'):
			self.model = self.load_model(self.modelfile)


		else:
			self.model = self.modelfile
# 			print("\nNo JAGS model was defined or selected. \
# Be sure to define a model before calling pyjags.Model")

	def load_model(self, filename:str) -> str:
		"""Load model file specified in spec string."""
		#TODO: clean up the logic around model specification.
		with open(os.path.join(os.getcwd(), filename), 'r') as modelfile:
			return modelfile.read()
	
	def set_model(self, model:str) -> None:
		"""Setter method for model"""
		self.model = model

	def configure(self, spec:str):
		"""Read spec string and bind all values needed for pyjags.Model
		
		Arguments:
			spec {str} -- a string representing the model specification
			(see ModelHandler.specification_template for expected format.)
		"""

		#TODO: Refactor this completely. It's nice to have the model spec look like
		#a simple settings file, but it's adding a lot of brittle complexity.
		#try to see who the users are, and whether this makes sense for them.
		#If so, rewrite it -- there are conventions for this kind of parsing,
		#and we're not really following them in this method.

		#initialize arguments to be passed to pyjags.Model
		self.modelfile = ''
		self.init = None
		self.samples = 1000
		self.chains = 4
		self.burnin = 1000
		self.thinning = 0
		self.data = {}
		self.sample = []
		self.seed = None
		self.adapt = 1000
		self.seed = None

		#Parse spec string
		#TODO: Create set method to adjust these settings outside the spec string
		section = ''
		for settingsline in spec.split('\n'):
			#throw out comments
			if "#" in settingsline:
				settingsline = settingsline.split("#")[0]
			settingsline = settingsline.rstrip()
				

			#detect section headers	
			if settingsline.endswith(':'):
				section = settingsline

			elif len(settingsline) > 0:
				if section == 'model:': #'model' in section:
					self.modelfile += settingsline + '\n'
				elif section == 'settings:':
					assignment = settingsline.replace(" ","").split('=')
					self.__dict__[assignment[0]] = assignment[1]
				elif section == 'data:':
					#break line into variable names and values
					assignment = settingsline.replace(" ","").split('=')
					expression = assignment[1]
					variables = assignment[0].split(',')
					#use regex to replace model variable names with names
					#appropriate for storage in the model.
					#This is NOT the clever way to do this, if it even should happen.
					for key in self.data.keys():
						expression = re.sub(fr'(\s{key}$|^{key}(?:\s|$)|\s{key}\s|\({key}\)|\[{key}\])',lambda match : (match.group(0).replace(str(key),f'self.data["{key}"]')), expression)
					#handle multiple variable assignment
					if len(variables) > 1:
						for index, variable in enumerate(variables):
							self.data[variable] = eval(expression)[index]
					#handle single variable assignment
					else:
						self.data[variables[0]] = eval(expression)
				elif section == 'sample:':
					self.sample.append(settingsline)
				

	def get_model_args(self):
		"""Create keyword arguments dictionary for pyjags.model.Model
		
		Raises:
			self.ModelSpecificationError -- Some required model parameter was not provided.
		
		Returns:
			dict -- a dictionary mapping parameters expected by pyjags.Model
			to the arguments specified in the model handler. This dict can be
			passed directly to the model using **kwargs syntax.
		"""
		self.data = {item:np.array(self.data[item]).astype('float') for item in self.data}
		if self.model == None:
			raise self.Error("Please define a model in the model specification \
			 string or using model_handler.set_model()")

		masked_data = {data_var:np.ma.masked_invalid(self.data[data_var]) for data_var in self.data}
		
		model_args = {'code':self.model,
			'init':self.init,
			'data': masked_data if len(masked_data) > 0 else None,
			'chains':int(self.chains),
		}

		if self.adapt == "auto":
			model_args['adapt'] = 0
		else:
			model_args['adapt'] = int(self.adapt)

		if self.seed != None and self.seed.lower() not in ('random', 'none'):
			model_args['init'] = {'.RNG.name':'base::Mersenne-Twister',
									'.RNG.seed': float(self.seed)}
		return model_args

	def get_sample_args(self) -> dict:
		"""Create keyword arguments dictionary for pyjags.model.Model.sample
		
		Returns:
			dict -- a dictionary mapping parameters expected by pyjags. Sample
			to the arguments specified in the model handler. This dict can be
			passed directly to the model using **kwargs syntax.
		"""
		sample_args = {'vars':self.sample,
			'iterations':int(self.samples),
		}
		if int(self.thinning) > 0:
			sample_args['thin'] = int(self.thinning)
		return sample_args

	def set_data(self, varname:str, value) -> None:
		"""Set model's data from outside the specification string.
		
		Arguments:
			varname {str} -- the model variable name you wish to assign
			value {int or list} -- the value to you wish a model variable to take
		"""
		self.data[varname] = value

	def init_chain(self, varname:str, init_values:list) -> None:
		"""Set the initial values of selected chain using values or a distribution.
		
		Arguments:
			varname {str} -- The name of a model variable whose initial value you wish\
			to fix.
			init_values {list, int, or string} -- If init_values is a list, each item\
in the list will be assigned to a chain. If single value, each chain will be initialized\
with that value. If string, value must indicate a distribution from numpy.random that produces\
a dingle number, e.g., `'uniform(0,5)'` or `'gamma(1,1)'`.
		
		Raises:
			self.Error -- Unacceptable values of `init_values` argument raise exceptions.
		"""
		#Note: It would be cool to know all of the model variables at this stage
		#but that would require some obscene parsing, a rework of the logic flow,
		#or a 'trial run' model initialization...

		self.chains = int(self.chains)

		if type(init_values) not in (np.ndarray, list, str, float, int):
			raise self.Error(f"ModelHandler.init_chain: expected initial values as list, \
int, float, or string representing numpy distribution. See help for usage.")

		if (type(init_values) in (np.ndarray, list) and
				len(init_values) != self.chains):
					raise self.Error(f"ModelHandler.init_chain: expected {self.chains} values\
(one per chain), but only received {len(init_values)}. If you wish to have all chains\
use same initial value, pass it as int, float, or distribution, rather than as a list.")


		if type(init_values) == str:
			source_distribution = lambda : eval('np.random.'+init_values)
			try:
				if type(source_distribution()) not in (float, int):
					raise self.Error(f"ModelHandler.init_chain: string input for init_values \
did not specify appropriate numpy.random distribution.")
			except:
				raise self.Error(f"ModelHandler.init_chain: Invalid string input for init_values. \
Argument must be string specifying an appropriate numpy.random distribution, e.g., 'uniform(0,1)'.")
			init_values = [source_distribution() for i in range(self.chains)]

		elif type(init_values) in (int, float):
			init_values = [init_values for i in range(self.chains)]

		if not self.init:
			self.init = [{varname:init_value} for init_value in init_values]

		else:
			new_init_list = [{varname:init_value} for init_value in init_values]
			self.init = [{**new_init_list[i], **self.init[i]} for i in range(len(self.init))]


	class Error(Exception):
		"""Raised when model specification parameters are incorrect."""
		pass