


from .HTMLElement import *




class HTML5HeadElement(HTMLElement):

	def __init__(self, proto, name):
		assert name == "head"
		super().__init__(proto, "head")
	#

	def __hasMetaTagWithCharset(self):
		for child in self.children:
			if isinstance(child, HTMLElement):
				if child.name == "meta":
					if "charset" in child.attributes:
						return True
		return False
	#

	def _serialize(self, outputBuffer:OutputBuffer):
		outputBuffer.write(self._openingTagData())

		if self._proto.bHasClosingTag:
			outputBuffer.incrementIndent()

			bRequireExtraCharsetTag = not self.__hasMetaTagWithCharset()
			if self.children or bRequireExtraCharsetTag:
				outputBuffer.newLine()
				if bRequireExtraCharsetTag:
					outputBuffer.writeLn("<meta charset=\"UTF-8\">")
				for child in self.children:
					if isinstance(child, (int, float, str)):
						outputBuffer.write(htmlEscape(str(child)))
					else:
						child._serialize(outputBuffer)
				outputBuffer.newLine()

			outputBuffer.decrementIndent()
			outputBuffer.write(self._closingTagData())

		else:
			if len(self.children) > 0:
				raise Exception("HTML tag \"" + self.name + "\" is not allowed to have child elements!")

		outputBuffer.newLine()
	#

#





