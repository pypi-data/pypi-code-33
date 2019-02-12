from spacy import tokens

ENTITY_TYPE_DESCRIPTION = {
	'org': 'organization',
	'gpe': 'geopolitical_entity'
}

class DocumentObject:
	def __init__(self, obj, document):
		"""
		:param obj: any object from a document
		:type document: Document
		"""
		self._obj = obj
		self._document = document

	@property
	def document(self):
		"""
		:rtype: Document
		"""
		return self._document

	def __repr__(self):
		return self._obj.__repr__()

	def __str__(self):
		return self._obj.__str__()

	def graph_str(self):
		return str(self)

	@property
	def id(self):
		return None

	def __eq__(self, other):
		return self.id==other.id

	def __ne__(self, other):
		return self.id!=other.id


class Span(DocumentObject):

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

	@property
	def type(self):
		"""
		:rtype: str
		"""
		if self.tokens[0]:
			try:
				return ENTITY_TYPE_DESCRIPTION[str(self.tokens[0].entity_type).lower()]
			except:
				return str(self.tokens[0].entity_type).lower()
		else:
			return self.tokens[0]


class NounChunk(Span):

	def __init__(self, obj, document):
		super().__init__(obj=obj, document=document)
		for token in self.tokens:
			token._noun_chunk = self

	@property
	def child_entities(self):
		return [e for e in self.document.entities if e.start >= self.start and e.end <= self.end]

	@property
	def parent_entities(self):
		return [e for e in self.document.entities if e.start < self.start and e.end > self.end]

	@property
	def entities(self):
		return self.parent_entities+self.child_entities

	@property
	def id(self):
		return (self.document.id, 'noun_chunk', self.start, self.end)

	def graph_str(self):
		return f'{self}'


class Entity(Span):

	def __init__(self, obj, document):
		super().__init__(obj=obj, document=document)
		for token in self.tokens:
			token._entity = self

	@property
	def name(self):
		return self._obj

	@property
	def parent_noun_chunks(self):
		return [nc for nc in self.document.noun_chunks if nc.start <= self.start and nc.end >= self.end]

	@property
	def child_noun_chunks(self):
		return [nc for nc in self.document.noun_chunks if nc.start > self.start and nc.end < self.end]

	@property
	def noun_chunks(self):
		return self.parent_noun_chunks+self.child_noun_chunks

	@property
	def id(self):
		return (self.document.id, 'entity', self.start, self.end)

	def graph_str(self):
		return f"{self}\n({str(self.type).replace('_', ' ')})"