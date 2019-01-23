

from .htmlgeneral import *
from .OutputBuffer import OutputBuffer




class HTMLRawCSS(object):

	def __init__(self, textOrTextList):
		if isinstance(textOrTextList, str):
			self.texts = [ textOrTextList ]
		else:
			self.texts = list(textOrTextList)
	#

	def __call__(self, **attrs):
		self.texts.append("".join(attrs))
		return self
	#

	def __getitem__(self, textOrTexts):
		if hasattr(type(textOrTexts), "__iter__"):
			self.texts.extend(textOrTexts)
		else:
			self.texts.append(textOrTexts)
		return self
	#

	def _serialize(self, outputBuffer:OutputBuffer):
		if self.texts:
			outputBuffer.newLine()
			outputBuffer.writeLn("<style type=\"text/css\">")
			outputBuffer.incrementIndent()
			for text in self.texts:
				outputBuffer.writeLn(text)
			outputBuffer.decrementIndent()
			outputBuffer.writeLn("</style>")
	#

#
