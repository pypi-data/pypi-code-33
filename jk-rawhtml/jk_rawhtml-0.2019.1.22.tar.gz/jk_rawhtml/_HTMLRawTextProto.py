

from .htmlgeneral import *
from .HTMLRawText import HTMLRawText




class _HTMLRawTextProto(object):

	def __init__(self, implClass=HTMLRawText):
		self.implClass = implClass
	#

	def __call__(self, *args, **attrs):
		return self.implClass(args)()
	#

	def __getitem__(self, children):
		return self.implClass("".join(children))
	#

#







