from ansiwrap import *
from collections.abc import *
from inspect import *
from numbers import *
from re import *
from shutil import *
from sys import *

_double = compile(r'__\w*[^_\W]').fullmatch
_magic = compile(r'__\w+__').fullmatch
_private = compile(r'_[^_\W]\w*').fullmatch

def hdir(obj, flags=''):
	flags = flags.replace('a', 'dmp')
	double = 'd' in flags
	magic = 'm' in flags
	private = 'p' in flags
	bold = '' if 'f' in flags else ';1'
	color = 'n' not in flags
	instance = vars(obj) if (
		not ismodule(obj) and
		not isclass(obj) and
		hasattr(obj, '__dict__') and
		type(vars(obj)) is dict) else {}
	abstract = obj.__abstractmethods__ if hasattr(obj, '__abstractmethods__') else ()

	def colorize(attr, value):
		c = ((1 if issubclass(value, BaseException) else 3) if isclass(value) else
			2 if isinstance(value, str) else
			4 if isinstance(value, Number) else
			5 if ismodule(value) else
			6 if isroutine(value) else '')
		return (f"\033[{c and f'3{c}{bold}'}{';3' if isabstract(value) or attr in abstract else ''}"
			f"{';4' if attr in instance else ''}m{attr}\033[m")

	def decorate(attr, value, prefix='', suffix=''):
		if isinstance(value, Collection):
			for cls, sym in (
					(str, "''"),
					(MutableSequence, '[]'),
					(Sequence, '()'),
					(Set, '{}'),
					(Mapping, '{}')):
				if isinstance(value, cls):
					prefix, suffix = prefix + sym[0], sym[1] + suffix
					if cls is str:
						break
					return decorate(attr, value.__iter__().__next__() if value else None, prefix, suffix)
		attr = prefix + attr + suffix
		return colorize(attr, value) if color else attr

	out = ' '.join([decorate(attr,value) for attr,value in sorted(getmembers(obj)) if
		(double or not _double(attr)) and (magic or not _magic(attr)) and (private or not _private(attr))])

	print(fill(out, width=get_terminal_size()[0]) if stdout.isatty() else out)