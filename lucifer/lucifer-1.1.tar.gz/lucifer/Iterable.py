from .ProgressBar import ProgressBar


class Iterable:
	def __init__(self, inner, progress_bar=None, text='', echo=True):
		"""
		:type inner: iterable
		:type progress_bar: ProgressBar
		:type text: str
		:type echo: bool
		"""
		self._idx = 0
		self._inner = inner
		self._text = text
		self._echo = echo
		if progress_bar is None:
			self._progress_bar = ProgressBar(total=len(self._inner))
		else:
			self._progress_bar = progress_bar
			self._progress_bar._total = len(self._inner)

	def __iter__(self):
		return self

	def __next__(self):
		self._idx += 1
		progress_amount = self._idx - 1
		try:
			if self._echo: self._progress_bar.show(amount=progress_amount, text=self._text)
			return self._inner[self._idx - 1]
		except IndexError:
			self._idx = 0
			raise StopIteration


def iterate(iterable, progress_bar=None, text='', echo=True):
	return Iterable(inner=iterable, progress_bar=progress_bar, text=text, echo=echo)

