

from .htmlgeneral import *
from .HTMLComment import HTMLComment




class _HTMLCommentProto(object):

	def __init__(self, implClass=HTMLComment):
		self.implClass = implClass
	#

	def __call__(self, *args, **attrs):
		return self.implClass(args)()
	#

	def __getitem__(self, children):
		return self.implClass("".join(children))
	#

#







