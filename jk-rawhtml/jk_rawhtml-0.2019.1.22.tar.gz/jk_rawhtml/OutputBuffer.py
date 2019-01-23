




class OutputBuffer(object):

	def __init__(self):
		self.__bIsNewLine = True		# are we at a new line position?
		self.__bHasContent = False		# do we already have content in this line?
		self.lines = []
		self.__buffer = []
		self.__indent = ""
	#

	def incrementIndent(self):
		# print("incrementIndent()")

		self.__indent += "\t"
	#

	def decrementIndent(self):
		# print("decrementIndent()")

		self.__indent = self.__indent[:-1]
	#

	def write(self, *items):
		# print("write( " + repr(items) + " )")

		if self.__bIsNewLine:
			self.__buffer.append(self.__indent)
			self.__bIsNewLine = False

		for item in items:
			if hasattr(type(item), "__iter__"):
				for i in item:
					if len(i) > 0:
						self.__buffer.append(i)
						self.__bHasContent = True
			else:
				if len(item) > 0:
					self.__buffer.append(item)
					self.__bHasContent = True
	#

	def writeLn(self, *items):
		# print("writeLn( " + repr(items) + " )")

		if self.__bIsNewLine:
			self.__buffer.append(self.__indent)
			self.__bIsNewLine = False

		for item in items:
			if hasattr(type(item), "__iter__"):
				for i in item:
					if len(i) > 0:
						self.__buffer.append(i)
						self.__bHasContent = True
			else:
				if len(item) > 0:
					self.__buffer.append(item)
					self.__bHasContent = True

		self.newLine()
	#

	def newLine(self):
		# print("newLine()")

		if not self.__bIsNewLine:
			if self.__bHasContent:
				self.lines.append("".join(self.__buffer))
				self.__bHasContent = False
			self.__buffer.clear()
			self.__bIsNewLine = True
	#

	def __str__(self):
		self.newLine()
		return "\n".join(self.lines)
	#

#



