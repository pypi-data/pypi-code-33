from .ModelHandler import ModelHandler
from .SampleHandler import SampleHandler

import pyjags

class SimpleSampler:
	def __init__(self, spec_string=None):
		if spec_string:
			self.model_spec = ModelHandler(spec_string)	

	def sample(self):
		self.pyjags_model = pyjags.Model(**self.model_spec.get_model_args())

		if self.model_spec.adapt == 'auto':
			while not self.pyjags_model.adapt(500):
				pass

		if int(self.model_spec.burnin) > 0:
			burnin_args = self.model_spec.get_sample_args()
			burnin_args['vars'] = None
			burnin_args['iterations'] = int(self.model_spec.burnin)

			print("Burn-in iterations (no samples recorded):")
			self.sample_data = self.pyjags_model.sample(**burnin_args)
			print("Sample iterations:")

		self.sample_data = self.pyjags_model.sample(**self.model_spec.get_sample_args())
		return SampleHandler(self.sample_data)

	def set_data(self, varname:str, value) -> None:
		self.model_spec.set_data(varname, value)

	def rebuild(self, spec_string):
		self.model_spec = ModelHandler(spec_string)