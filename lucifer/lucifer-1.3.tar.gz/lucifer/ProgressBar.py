from sys import stdout
from datetime import datetime
import pandas as pd
_map = map

try:
	from slytherin.colour import colour
except:
	from .colour import colour

class ProgressBar:
	def __init__(
			self, total, bar_length = 20, bar_full = '▓', bar_empty = '▒', animation='clock',
			full_colour='blue', empty_colour='grey', text_colour='grey', next_line = True
	):
		self._total = total
		self._bar_length = bar_length
		self._bar_full = bar_full
		self._bar_empty = bar_empty
		self._start_time = datetime.now()
		self._animation_counter = -1
		if animation == 'vertical_bar':
			animation_clips = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
			animation_clips = animation_clips + animation_clips[::-1]
		elif animation == 'ball':
			animation_clips = ['⠁', '⠂', '⠄', '⡀', '⢀', '⠠', '⠐', '⠈']
		elif animation == 'clock':
			animation_clips = ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛']
		elif animation == 'big_ball':
			animation_clips = ['●    ', '●    ', ' ●   ', ' ●   ', '  ●  ', '   ● ', '   ● ', '    ●', '    ●']
			animation_clips = animation_clips + animation_clips[::-1]
		elif animation == 'line':
			animation_clips = ['\\', '|', '/', '-']
		else:
			animation_clips = None
		self._animation_clips = animation_clips
		self._full_colour = full_colour
		self._empty_colour = empty_colour
		self._text_colour = text_colour
		self._next_line = next_line
		self._completed = False
		self._max_length = 0

	@property
	def animation(self):
		if self._animation_clips is None:
			return ''
		else:
			self._animation_counter += 1
			return self._animation_clips[self._animation_counter % len(self._animation_clips)] + ' '

	def complete(self):
		self._completed = True

	@property
	def completed(self):
		return self._completed

	def get_percent(self, amount):
		return amount / self._total * 100

	def format_percent(self, amount):
		amount = min(amount, self._total)
		formatted_percent = '{0: >#06.2f}'.format(float(self.get_percent(amount=amount))) + '%'
		return formatted_percent

	def get_elapsed_seconds(self):
		delta = datetime.now() - self._start_time
		delta_seconds = delta.seconds + delta.microseconds / 1E6
		return delta_seconds

	def get_remaining_seconds(self, amount):
		amount = min(amount, self._total)
		delta_seconds = self.get_elapsed_seconds()

		try:
			speed = amount/delta_seconds
		except:
			speed = None
		if amount>=self._total:
			return 0
		else:
			try:
				the_time = (self._total - amount) / speed
			except:
				the_time = None
			return the_time

	@staticmethod
	def format_time(time):
		"""
		:type time: float or int
		:rtype: str
		"""
		# convert to the right unit
		if time is None:
			return ''
		else:
			if time > 3600:
				unit = 'h'
				time = time/3600
			elif time > 60:
				unit = 'm'
				time = time/60
			else:
				unit = 's'
				time = time

			return '{0: >#04.1f}'.format(float(time))+unit

	def format_bar(self, amount):
		"""
		:type amount: int or float
		:rtype: str
		"""
		amount = min(amount, self._total)
		full_part_len = round(amount*self._bar_length/self._total)
		empty_part_len = self._bar_length - full_part_len

		if self._full_colour is not None:
			character = '▅' # character = self._bar_empty
			full_part = colour(text=character * full_part_len, text_colour=self._full_colour)
			empty_part = colour(text=character * empty_part_len, text_colour=self._empty_colour)
		else:
			full_part = self._bar_full * full_part_len
			empty_part = self._bar_empty * empty_part_len

		return full_part + empty_part

	def write(self, string):
		"""
		:type string: str
		"""
		stdout.write('\r'+string)

	def show(self, amount, percent=True, bar=True, time=True, text=''):
		"""
		:type amount: int or float
		:type percent: bool
		:type bar: bool
		:type time: bool
		:type text: str
		"""
		string = ''
		length = 0
		animation = self.animation; length += len(animation)
		string += colour(text=animation, text_colour=self._empty_colour)
		if time:
			remaining = self.get_remaining_seconds(amount=amount)
			elapsed = self.get_elapsed_seconds()
			elapsed_text = f'e:{self.format_time(elapsed)} '.ljust(10)
			remaining_text = f'r:{self.format_time(remaining)} '.ljust(10)
			string += colour(text=elapsed_text, text_colour=self._full_colour)
			string += colour(text=remaining_text, text_colour=self._empty_colour)
			length += len(elapsed_text) + len(remaining_text)

		if bar:
			bar_coloured = self.format_bar(amount=amount)
			string += bar_coloured
			length += self._bar_length
		if percent:
			percent_text = (' ' + self.format_percent(amount=amount)).rjust(8)
			string += colour(text=percent_text, text_colour=self._full_colour)
			length += len(percent_text)

		string += ' ' + colour(text=text, text_colour=self._text_colour)
		length += 1 + len(text)

		if self._max_length < length:
			self._max_length = length
		padding = ' '*(self._max_length-length)
		self.write(string=string+padding)
		stdout.flush()
		if amount == self._total: self.complete()
		if self._next_line and self._completed:
			print('')


	@classmethod
	def map(
			cls,function, iterable, progress_step=None, percent=True, bar=True, time=True, text='', echo=1,
			next_line = True, iterable_text=None,
			**kwargs
	):
		echo = max(0, echo)
		def _func(x, _progress, _progress_bar, _text=''):
			if progress['amount'] == 0:
				progress_bar.show(amount=progress['amount'], percent=percent, bar=bar, time=time, text=text+_text)
			result = function(x)
			_progress['amount'] += 1
			if _progress['max_step'] > 1:
				if _progress['amount'] % _progress['step'] == 0 or _progress['amount'] >= total:
					_progress_bar.show(amount=_progress['amount'], percent=percent, bar=bar, time=time, text=text+_text)
					_progress['step'] = min(_progress['step'] * 2, _progress['max_step'])
			else:
				_progress_bar.show(amount=_progress['amount'], percent=percent, bar=bar, time=time, text=text+_text)
			return result

		total = len(iterable)
		if progress_step is None:
			progress_step = max(round(total / 10), 1)  # we don't want progress step to be 0
		progress = {'amount': 0, 'step': 1, 'max_step': progress_step}
		progress_bar = cls(total=total, next_line=next_line, **kwargs)
		if echo:
			if iterable_text is None:
				result = _map(
					lambda x: _func(x=x, _progress=progress, _progress_bar=progress_bar),
					iterable
				)
			else:
				result = _map(
					lambda x: _func(x=x[0], _text=x[1], _progress=progress, _progress_bar=progress_bar),
					zip(iterable, iterable_text)
				)

			return result
		else:
			return _map(function, iterable)

	@classmethod
	def apply(
			cls, function, data=None, series=None, progress_step=None, percent=True, bar=True, time=True, text='',
			axis=1, echo=1, next_line=True, **kwargs
	):
		"""
		:type function: function
		:type data: pd.DataFrame
		:type series: pd.Series
		:type progress_step: int
		:type percent: bool
		:type bar: bool
		:type time: bool
		:type text: str
		:type axis: int
		:type echo: bool
		:type next_line: bool
		:rtype: pd.DataFrame or pd.Series
		"""
		echo = max(0, echo)
		# either data or series should be provided:
		if data is None and series is None: raise ValueError('either data or series should be provided')
		if data is not None and series is not None: raise ValueError('both data and series cannot be provided')
		def _func(x, progress, progress_bar):
			result = function(x)
			progress['amount'] += 1
			if progress['max_step'] > 1:
				if progress['amount'] % progress['step'] == 0 or progress['amount'] >= total:
					progress_bar.show(amount=progress['amount'], percent=percent, bar=bar, time=time, text=text)
					progress['step'] = min(progress['step'] * 2, progress['max_step'])
			else:
				progress_bar.show(amount=progress['amount'], percent=percent, bar=bar, time=time, text=text)
			return result
		if data is not None:
			if axis == 1:
				total = data.shape[0]
			else:
				total = data.shape[1]
		else:
			total = series.shape[0]

		if total == 0:
			return None

		if progress_step is None:
			progress_step = max(round(total / 10), 1)  # we don't want progress step to be 0
		progress = {'amount': 0, 'step': 1, 'max_step': progress_step}
		progress_bar = cls(total=total, next_line=next_line, **kwargs)
		if echo:
			progress_bar.show(amount=0, percent=percent, bar=bar, time=time, text=text)
			if data is not None:
				result = data.apply(func=lambda x: _func(x=x, progress=progress, progress_bar=progress_bar), axis=axis)
			else:
				result = series.apply(func=lambda x: _func(x=x, progress=progress, progress_bar=progress_bar))
			return result
		else:
			if data is not None:
				return data.apply(func=function, axis=axis)
			else:
				return series.apply(func=function)


Progress = ProgressBar








