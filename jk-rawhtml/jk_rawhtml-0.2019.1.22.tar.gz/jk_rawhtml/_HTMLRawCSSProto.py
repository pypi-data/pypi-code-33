

from .htmlgeneral import *
from .HTMLRawCSS import HTMLRawCSS




class _HTMLRawCSSProto(object):

	def __init__(self, implClass=HTMLRawCSS):
		self.implClass = implClass
	#

	def __call__(self, *args, **attrs):
		return self.implClass(args)()
	#

	def __getitem__(self, children):
		return self.implClass(children)
	#

#







