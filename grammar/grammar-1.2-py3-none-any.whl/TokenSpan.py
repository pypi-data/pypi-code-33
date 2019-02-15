from .DocumentObject import DocumentObject

from spacy import tokens

class TokenSpan(DocumentObject):

	@property
	def obj(self):
		"""
		:rtype: tokens.Span
		"""
		return self._obj

	@property
	def start(self):
		"""
		:rtype: int
		"""
		return self.obj.start

	@property
	def end(self):
		"""
		:rtype: int
		"""
		return self.obj.end

	@property
	def id(self):
		return (self.document.id, 'span', self.start, self.end)

	@property
	def text(self):
		"""
		:rtype: str
		"""
		return self.obj.text


	@property
	def tokens(self):
		"""
		:rtype: list[Token]
		"""
		return self.document.tokens[self.start:self.end]




