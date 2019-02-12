from .DocumentObject import NounChunk, Entity
from .Token import Token

from vineyard import Graph, NodeStyle
import spacy

nlp = spacy.load('en_core_web_sm')

class Document:
	def __init__(self, text, id=0):
		"""
		:type text: str
		"""
		self._id = id
		self._text = str(text)
		self._doc = nlp(self._text)
		self._tokens = [Token(obj=x, document=self) for x in self.doc]
		self._noun_chunks = [NounChunk(span, document=self) for span in self.doc.noun_chunks]
		self._entities = [Entity(obj=span, document=self) for span in self.doc.ents]
		self._entity_graph = None
		self._graph = None

	@property
	def id(self):
		return self._id

	@property
	def doc(self):
		"""
		:rtype: tokens.Doc
		"""
		return self._doc

	def __repr__(self):
		return self.doc.__repr__()

	def __str__(self):
		return self.doc.__str__()

	def graph_str(self):
		return f'd: {self}'[0:50]


	@property
	def tokens(self):
		return self._tokens

	@property
	def entities(self):
		"""
		:rtype: list[Entity]
		"""
		return self._entities

	@property
	def noun_chunks(self):
		"""
		:rtype: list[NounChunk]
		"""
		return self._noun_chunks

	@property
	def entity_graph(self):
		if self._entity_graph is None:
			graph = Graph(ordering=False)
			"""
			graph.add_node(
				name=str(self.id), label=self.graph_str(),
				style=NodeStyle(shape='rect', style='"rounded, filled"', fill_colour='dodgerblue4', text_colour='white')
			)
			"""

			tokens = []
			for token in self.tokens:
				if token not in tokens:
					tokens.append(token)
					graph.add_node(
						name=str(token.id), label=f'{token.graph_str()}',
						style=NodeStyle(text_size=8, shape='rect', style='"rounded, filled"')
					)

			noun_chunks = []
			for noun_chunk in self.noun_chunks:
				if noun_chunk not in noun_chunks:
					noun_chunks.append(noun_chunk)
					graph.add_node(
						name=str(noun_chunk.id), label=f'{noun_chunk.graph_str()}',
						style=NodeStyle(
							fill_colour='lightpink', text_colour='black', text_size=8,
							shape='rect', style='"rounded, filled"'
						)
					)
					# connect to document
					#graph.connect(start=str(self.id), end=str(noun_chunk.id))

			for token in tokens:
					if token.noun_chunk:
						graph.connect(start=str(token.noun_chunk.id), end=str(token.id))
					#else:
					#	graph.connect(start=str(self.id), end=str(token.id))


			entities = []
			for entity in self.entities:
				if entity not in entities:
					entities.append(entity)
					graph.add_node(
						name=str(entity.id), label=f'{entity.graph_str()}',
						style=NodeStyle(fill_colour='gold', text_colour='black')
					)
					for token in entity.tokens:
						graph.connect(start=str(token.id), end=str(entity.id))


			self._entity_graph = graph
		return self._entity_graph

	@property
	def graph(self):
		if self._graph is None:
			graph = Graph(ordering=False)
			for token in self.tokens:
				graph.add_node(name=str(token.id), label=token.graph_str())
			for token in self.tokens:
				for child in token.children:
					dependency_label = str(child.dependency).replace('_', '\n')
					graph.connect(start=str(token.id), end=str(child.id), label=dependency_label)
			self._graph = graph
		return self._graph
