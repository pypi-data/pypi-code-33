from abc import ABC, abstractmethod

class BaseMixin(ABC):

	@abstractmethod
	def get_example(self, i):
		s = super(BaseMixin, self)
		if hasattr(s, "get_example"):
			return s.get_example(i)

	def __getitem__(self, i):
		return self.get_example(i)
