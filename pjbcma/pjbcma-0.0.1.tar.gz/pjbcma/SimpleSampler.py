import ModelHandler
import SampleHandler

class SimpleSampler:
	def __init__(self, spec_string=None):
		if spec_string:
			self.model_spec = ModelHandler(spec_string)	

	def sample(self):
		self.pyjags_model = pyjags.Model(**self.model_spec.get_model_args())
		self.sample_data = self.pyjags_model.sample(**self.model_spec.get_sample_args())
		return SampleHandler(self.sample_data)

	def set_data(self, varname:str, value) -> None:
		self.model_spec.set_data(varname, value)

	def rebuild(self, spec_string):
		self.model_spec = ModelHandler(spec_string)