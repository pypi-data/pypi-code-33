from ansiwrap import *
from collections.abc import *
from inspect import *
from numbers import *
from re import *
from shutil import *
from sys import *
from types import *

__all__ = ('hdir',)

_double = compile(r'__\w*[^_\W]').fullmatch
_magic = compile(r'__\w+__').fullmatch
_private = compile(r'_[^_\W]\w*').fullmatch
_no = []

def hdir(obj=_no, flags=''):
	flags = flags.replace('a', 'dmp')
	double = 'd' in flags
	magic = 'm' in flags
	private = 'p' in flags
	color = 'n' not in flags

	def abstract(attr, value):
		return isabstract(value) or attr in abstractmethods

	def colorize(attr, value, style):
		c = ((1 if issubclass(value, BaseException) else 3) if isclass(value) else
			2 if isinstance(value, str) else
			4 if isinstance(value, Number) else
			5 if ismodule(value) else
			6 if isroutine(value) else '')
		return ('\033[' + (c and f"3{c}{'' if '3' in style or '<' in attr else ';1'}") +
			f'{style}m{attr}\033[m')

	def decorate(attr, value, style, prefix='', suffix=''):
		if isinstance(value, Collection):
			for cls, sym in (
					(str, "''"),
					(MutableSequence, '[]'),
					(Sequence, '()'),
					(Set, '{}'),
					(MappingProxyType, ('<{', '}>')),
					(Mapping, '{}')):
				if isinstance(value, cls):
					prefix, suffix = prefix + sym[0], sym[1] + suffix
					if cls is str:
						break
					item = next(iter(value)) if value else None
					return decorate(attr,
						value[item] if value and isinstance(value, Mapping) else item,
						style, prefix, suffix)
		if (ismethoddescriptor(value) or isdatadescriptor(value) or
			isgetsetdescriptor(value) or ismemberdescriptor(value)):
			prefix, suffix = prefix + '<', '>' + suffix
		if (isfunction(value) or ismethod(value)) and '3' not in style:
			suffix = '()' + suffix
		attr = prefix + attr + suffix
		return colorize(attr, value, style) if color else attr

	if obj is _no:
		out = ('\033[3mabstract\033[m \033[33;1mclass\033[m {dict} \033[31;1mexception\033[m '
			'\033[36;1mfunction\033[m \033[4minstance\033[m [list] \033[35;1mmodule\033[m '
			"\033[34;1mnumber\033[m other \033[36;1mpython()\033[m {set} \033[32;1m'string'\033[m "
			'(tuple) \033[36m<wrapper>\033[m' if color else
			"{dict} [list] other python() {set} 'string' (tuple) <wrapper>")
	else:
		abstractmethods = obj.__abstractmethods__ if hasattr(obj, '__abstractmethods__') else ()
		items = sorted([(attr, value) for attr, value in getmembers(obj) if
			hasattr(obj, attr) and (abstract(attr, value) or
				(double or not _double(attr)) and
				(magic or not _magic(attr)) and
				(private or not _private(attr)))])
		if 'r' in flags:
			return dict(items)
		instance = vars(obj) if (
			not ismodule(obj) and
			not isclass(obj) and
			hasattr(obj, '__dict__') and
			type(vars(obj)) is dict) else {}
		out = ' '.join([decorate(attr, value,
			(';3' if abstract(attr, value) else '') + (';4' if attr in instance else ''))
			for attr, value in items])

	print(fill(out, width=get_terminal_size()[0]) if stdout.isatty() else out)