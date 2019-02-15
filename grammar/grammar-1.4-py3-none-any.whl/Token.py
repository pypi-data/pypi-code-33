from .DocumentObject import DocumentObject
from .dependency_definitions import DEPENDENCY_DEFINITONS


class Token(DocumentObject):
	def __init__(self, obj, document):
		"""
		:param obj: any object from a document
		:type document: Document
		"""
		super().__init__(obj=obj, document=document)
		self._entity = None
		self._noun_chunk = None
		self._parents = None
		self._children = None

	@property
	def index(self):
		"""
		:rtype: int
		"""
		return self.token.i

	def graph_str(self):
		return f"[{self.index}] '{self}'\n{self.part_of_speech.replace('_', ' ')}"

	@property
	def id(self):
		"""
		:rtype: tuple
		"""
		return (self.document.id, 'token', self.index)

	@property
	def token(self):
		"""
		:rtype: tokens.Token
		"""
		return self._obj

	@property
	def text(self):
		return self.token.text

	@property
	def lemma(self):
		return self.token.lemma_

	@property
	def part_of_speech(self):
		"""
		:rtype: str
		"""
		try:
			return PART_OF_SPEACH[str(self.token.pos_).lower()]
		except:
			if self.token.pos_:
				return str(self.token.pos_).lower()
			else:
				return self.token.pos_

	@property
	def tag(self):
		return self.token.tag_

	@property
	def dependency_code(self):
		"""
		:rtype: str
		"""
		return self.token.dep_

	@property
	def dependency(self):
		"""
		:rtype: str
		"""
		try:
			return DEPENDENCY_DEFINITONS[self.dependency_code.lower()]
		except:
			return self.dependency_code

	@property
	def shape(self):
		return self.token.shape_

	@property
	def is_alpha(self):
		return self.token.is_alpha

	@property
	def is_stop(self):
		return self.token.is_stop



	@property
	def entity_iob(self):
		return self._obj.ent_iob_

	@property
	def entity_type(self):
		return self._obj.ent_type_

	@property
	def entity(self):
		"""
		:rtype: Entity
		"""
		return self._entity

	@property
	def noun_chunk(self):
		"""
		:rtype: NounChunk
		"""
		return self._noun_chunk

	@property
	def parents(self):
		"""
		:rtype: list[Token]
		"""
		if self._parents is None:
			self._parents = [Token(obj=x, document=self.document) for x in self.token.ancestors]
		return self._parents

	@property
	def children(self):
		"""
		:rtype: list[Token]
		"""
		if self._children is None:
			self._children = [Token(obj=x, document=self.document) for x in self.token.children]
		return self._children