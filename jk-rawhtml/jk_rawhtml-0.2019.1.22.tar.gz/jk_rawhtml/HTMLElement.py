


from .OutputBuffer import OutputBuffer
from .htmlgeneral import *
from .CSSMap import CSSMap




class HTMLElement(object):

	def __init__(self, proto, name):
		self.name = name
		self.attributes = {}
		self.children = []
		self._proto = proto
	#

	def addAttributes(self, **attrs):
		for k, v in attrs.items():
			if k.startswith("_"):
				self.attributes[k[1:]] = v
			else:
				self.attributes[k] = v
		return self
	#

	def addContent(self, *args):
		self.children.extend(args)
		return self
	#

	"""
	def addChildren(self, *args):
		self.children.extend(args)
		return self
	#
	"""

	def __call__(self, **attrs):
		assert not self.attributes
		for k, v in attrs.items():
			if k.startswith("_"):
				self.attributes[k[1:]] = v
			else:
				self.attributes[k] = v
		return self
	#

	def __getitem__(self, childOrChildren):
		if hasattr(type(childOrChildren), "__iter__"):
			self.children.extend(childOrChildren)
		else:
			self.children.append(childOrChildren)
		return self
	#

	def _openingTagData(self):
		ret = [ "<", self.name ]
		self._attrsToStr(ret)
		ret.append(">")
		return ret
	#

	def _attrsToStr(self, ret:list):
		for k, v in self.attributes.items():
			if k == "style":
				if isinstance(v, str):
					v = v.strip()
					if v:
						ret.extend((" style=\"", v, "\""))
				elif isinstance(v, CSSMap):
					if v:
						ret.extend((" style=\"", str(v), "\""))
				else:
					raise Exception("Unexpected value specified for HTML tag attribute '" + k + "': type " + str(type(v)) + ", value " + repr(v))
			else:
				if isinstance(v, (int, float)):
					ret.extend((" ", k, "=\"", str(v), "\""))
				elif isinstance(v, str):
					ret.extend((" ", k, "=\"", htmlEscape(v), "\""))
				else:
					raise Exception("Unexpected value specified for HTML tag attribute '" + k + "': type " + str(type(v)) + ", value " + repr(v))
	#

	def _closingTagData(self):
		return [ "</", self.name, ">" ]
	#

	def __str__(self):
		buf = OutputBuffer()
		self._serialize(buf)
		return str(buf)
	#

	def _serialize(self, outputBuffer:OutputBuffer):
		if self._proto.bLineBreakOuter:
			outputBuffer.newLine()
		outputBuffer.write(self._openingTagData())

		if self._proto.bHasClosingTag:
			outputBuffer.incrementIndent()
			if self._proto.bLineBreakInner:
				if self.children:
					outputBuffer.newLine()
					for child in self.children:
						if isinstance(child, (int, float, str)):
							outputBuffer.write(htmlEscape(str(child)))
						else:
							child._serialize(outputBuffer)
					outputBuffer.newLine()
			else:
				for child in self.children:
					if isinstance(child, (int, float, str)):
						outputBuffer.write(htmlEscape(str(child)))
					else:
						child._serialize(outputBuffer)

			outputBuffer.decrementIndent()
			outputBuffer.write(self._closingTagData())

		else:
			if len(self.children) > 0:
				raise Exception("HTML tag \"" + self.name + "\" is not allowed to have child elements!")

		if self._proto.bLineBreakOuter:
			outputBuffer.newLine()
	#

#





