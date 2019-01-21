import itertools
import pandas as pd
from pandas import Series

from .queries import *
from .client import Client

__author__ = "Aisha Mohamed <ahmohamed@qf.org.qa>"


class RDFGraphDataset(object):
	"""
	A class for loading and processing RDF datasets for relational learning models
	It provides some convenience functions for accessing a knowldge graph from a sparql endpoint
	"""

	def __init__(self, sparql_endpoint, graph_name=None):
		"""
		Initialize the RDFGraphDataset class.
		Each graph has to create a new RDFGraphDataset dataset.
		:param sparql_endpoint: string representing the sparql endpoint URI
		:param graph_name: string representing the dataset URI. if no graph_name is passed,
		the sparql queries will not contain FROM clause
		"""
		super(RDFGraphDataset, self).__init__()
		self.graph = graph_name
		self.endpoint = sparql_endpoint
		self.client = Client(self.endpoint)
		self.entity2idx = None
		self.predicate2idx = None
		self.relation2idx = None
		self.attribute2idx = None
		self.attribute_literal_pair2idx = None

	def num_entities(self):
		"""
		:return: integer representing the number of entities
		"""
		query_string = str(NEntities(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_predicates(self):
		"""
		:return: integer representing the number of relations
		"""
		query_string = str(NPredicates(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_relations(self):
		"""
		:return: integer representing the number of relations
		"""
		query_string = str(NRelations(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_attributes(self):
		"""
		:return: integer representing the number of attributes
		"""
		query_string = str(NAttributes(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_attr_literal_pairs(self):
		"""
		:return: integer representing the number of attribute literal pairs
		"""
		query_string = str(NAttributeLiteralPairs(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_triples(self):
		"""
		:return: integer representing the number of triples
		"""
		query_string = str(NTriples(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_entity2entity_triples(self):
		"""
		:return: integer representing the number of entity to entity triples
		"""
		query_string = str(NE2ETriples(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_entity2literal_triples(self):
		"""
		:return: integer representing the number of entity to literal triples
		"""
		query_string = str(NE2LTriples(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def num_rdf_type_triples(self):
		query_string = str(NRDFTTypeTriples(self.graph))
		result = self.client.execute_query(query_string, limit=1)
		result = result.values.tolist()[0][0]
		return result

	def entities(self, return_format='dict'):
		"""
		A function that returns the entities in the graph
		:param return_format: one of ['dict', 'df', 'list']
		:return: the entities in the knowledge graph represented in the specified return format
		"""
		query_string = str(Entities(self.graph))
		result_df = self.client.execute_query(query_string)
		# set the column name to "entity"
		result_df.columns = ['entity']
		# create a new column for the index
		result_df.reset_index(level=0, inplace=True)
		entity2idx = Series(result_df['index'].values, index=result_df['entity'].values).to_dict()
		self.entity2idx = entity2idx

		if return_format == 'dict':
			return entity2idx
		elif return_format == 'df':
			return result_df
		elif return_format == 'list':
			return list(itertools.chain(*result_df.values))

	def predicates(self, return_format='dict'):
		"""
		A function that returns the predicates in the graph
		:param return_format: one of ['dict', 'df', 'list']
		:return: the predicates in the knowledge graph represented in the specified return format
		"""
		query_string = str(Predicates(self.graph))
		result_df = self.client.execute_query(query_string)
		# set the column name to "predicate"
		result_df.columns = ['predicate']
		# create a new column for the index
		result_df.reset_index(level=0, inplace=True)
		# convert it to a dictionary and store it
		predicate2idx = Series(result_df['index'].values, index=result_df['predicate'].values).to_dict()
		self.predicate2idx = predicate2idx

		if return_format == 'dict':
			return predicate2idx
		elif return_format == 'df':
			return result_df
		elif return_format == 'list':
			return result_df['predicate'].values	

	def relations(self, return_format='dict'):
		"""
		A function that returns the relations in the graph
		:param return_format: one of ['dict', 'df', 'list']
		:return: the relations in the knowledge graph represented in the specified return format
		"""
		query_string = str(Relations(self.graph))
		result_df = self.client.execute_query(query_string)
		# set the column name to "relation"
		result_df.columns = ['relation']
		# create a new column for the index
		result_df.reset_index(level=0, inplace=True)
		relation2idx = Series(result_df['index'].values, index=result_df['relation'].values).to_dict()
		self.relation2idx = relation2idx

		if return_format == 'dict':
			return relation2idx
		elif return_format == 'df':
			return result_df
		elif return_format == 'list':
			return list(itertools.chain(*result_df.values))

	def attributes(self, return_format='dict'):
		"""
		A function that returns the attributes in the graph
		:param return_format: one of ['dict', 'df', 'list']
		:return: the attributes in the knowledge graph represented in the specified return format		
		"""
		query_string = str(Attributes(self.graph))
		result_df = self.client.execute_query(query_string)
		# set the column name to "attribute"
		result_df.columns = ['attribute']
		# create a new column for the index
		result_df.reset_index(level=0, inplace=True)
		attribute2idx = Series(result_df['index'].values, index=result_df['attribute'].values).to_dict()
		self.attribute2idx = attribute2idx

		if return_format == 'dict':
			return attribute2idx
		elif return_format == 'df':
			return result_df
		elif return_format == 'list':
			return list(itertools.chain(*result_df.values))

	def attr_literal_pairs(self, return_format='dict'):
		"""
		A function that returns the attribute literal pairs in the graph
		:param return_format: one of ['dict', 'df', 'list']
		:return: the attribute literal pairs in the knowledge graph represented in the specified return format
		"""
		query_string = str(AttributeLiteralPairs(self.graph))
		result_df = self.client.execute_query(query_string)
		# set the column name to "attribute_literal_pair"
		result_df.columns = ['attribute', 'literal']
		result_df["attribute_literal_pair"] = result_df["attribute"] + result_df["literal"].map(str)

		#result_df['attribute_literal_pair'] = result_df[['attribute', 'literal']].apply(lambda x: ','.join(str(x)), axis=1)
		print("IN attr_literal_pairs", result_df.columns)
		print("IN attr_literal_pairs", result_df.head())
		# create a new column for the index
		result_df.reset_index(level=0, inplace=True)
		attribute_literal_pair2idx = Series(result_df['index'].values, index=result_df['attribute_literal_pair'].values).to_dict()
		self.attribute_literal_pair2idx = attribute_literal_pair2idx

		if return_format == 'dict':
			return attribute_literal_pair2idx
		elif return_format == 'df':
			return result_df
		elif return_format == 'list':
			return list(itertools.chain(*result_df.values))

	def triples(self, entity2idx=None, predicate2idx=None, return_format='list'):
		"""
		A function that returns all the triples in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param predicate2idx: a dictionary mapping each entity in the graph to an index from 0 to n_predicates-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
		query_string = str(Triples(self.graph))
		result_df = self.client.execute_query(query_string)
		result_df.columns = ['subject', 'object', 'predicate']
		# find the dictionary mapping each entity to its index
		if entity2idx is None:
			if self.entity2idx is None:
				entity2idx = self.entities('dict')
			else:
				entity2idx = self.entity2idx
		# find the dictionary mapping each predicate to its index
		if predicate2idx is None:
			if self.predicate2idx is None:
				predicate2idx = self.predicates('dict')
			else:
				predicate2idx = self.predicate2idx
		# map the entities and predicates to their indices
		result_df.replace({'subject': entity2idx}, inplace=True)
		result_df.replace({'object': entity2idx}, inplace=True)
		result_df.replace({'predicate': predicate2idx}, inplace=True)

		if return_format == 'list':
			return result_df.values.tolist()
		elif return_format == 'df':
			return result_df

	def entity2entity_triples(self, entity2idx=None, relation2idx=None, return_format='list'):
		"""
		A function that returns all the entity2entity triples in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param relation2idx: a dictionary mapping each entity in the graph to an index from 0 to n_relations-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
		query_string = str(E2ETriples(self.graph))
		result_df = self.client.execute_query(query_string)
		rdf_triples_df = self.client.execute_query(str(RDFTTypeTriples(self.graph)))
		# find the dictionary mapping each entitt to its index
		if entity2idx is None:
			if self.entity2idx is None:
				entity2idx = self.entities('dict')
			else:
				entity2idx = self.entity2idx
		# find the dictionary mapping each relation to its index
		if relation2idx is None:
			if self.relation2idx is None:
				relation2idx = self.relations('dict')
			else:
				relation2idx = self.relation2idx

		# rearrange columns to be subject, object, relation
		result_df.columns = ['subject', 'predicate', 'object']
		rdf_triples_df.columns = ['subject', 'predicate', 'object']
		result_df = pd.concat([result_df, rdf_triples_df], ignore_index=True)
		#result_df = result_df[['subject', 'object', 'predicate']]
		# map the subjects to their indices
		result_df = result_df.replace({'subject': entity2idx})
		result_df = result_df.replace({'object': entity2idx})
		result_df = result_df.replace({'predicate': relation2idx})

		if return_format == 'list':
			return result_df.values.tolist()
		elif return_format == 'df':
			return result_df

	def entity2literal_triples(self, entity2idx=None, attribute_literal_pair2idx=None, return_format='list'):
		"""
		A function that returns all the entity2literal triples in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param attribute_literal_pair2idx: a dictionary mapping each entity in the graph to an index from 0 to
		n_relations-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
		query_string = str(E2LTriples(self.graph))
		result_df = self.client.execute_query(query_string)
		# find the dictionary mapping each entity to its index
		if entity2idx is None:
			if self.entity2idx is None:
				entity2idx = self.entities('dict')
			else:
				entity2idx = self.entity2idx
		# find the dictionary mapping each predicate,literal pair to its index
		if attribute_literal_pair2idx is None:
			if self.attribute_literal_pair2idx is None:
				attribute_literal_pair2idx = self.attr_literal_pairs('dict')
			else:
				attribute_literal_pair2idx = self.attribute_literal_pair2idx

		result_df.columns = ['subject', 'predicate', 'object']
		result_df['attribute_literal_pair'] = result_df[['predicate', 'object']].apply(lambda x: ','.join(str(x)), axis=1)

		# map the subjects to their indices
		result_df = result_df.replace({'subject': entity2idx})
		result_df = result_df.replace({'attribute_literal_pair': attribute_literal_pair2idx})

		if return_format == 'list':
			return result_df.values.tolist()
		elif return_format == 'df':
			return result_df

	def subjects(self, p, entity2idx=None, return_format='list'):
		"""
		A function that returns all the subjects of predicate p in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
		query_string = str(Subjects(self.graph, p))
		result_df = self.client.execute_query(query_string)
		# find the dictionary mapping each entity to its index
		if entity2idx is None:
			if self.entity2idx is None:
				entity2idx = self.entities('dict')
			else:
				entity2idx = self.entity2idx

		result_df.columns = ['subject']
		# map the subjects to their indices
		result_df = result_df.replace({'subject': entity2idx})

		if return_format == 'list':
			return result_df.values.tolist()
		elif return_format == 'df':
			return result_df

	def objects(self, p, entity2idx=None, return_format='list'):
		"""
		A function that returns all the objects of predicate p in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
		query_string = str(Objects(self.graph, p))
		result_df = self.client.execute_query(query_string)
		# find the dictionary mapping each entity to its index
		if entity2idx is None:
			if self.entity2idx is None:
				entity2idx = self.entities('dict')
			else:
				entity2idx = self.entity2idx

		result_df.columns = ['object']
		# map the subjects to their indices
		result_df = result_df.replace({'object': entity2idx})

		if return_format == 'list':
			return result_df.values.tolist()
		elif return_format == 'df':
			return result_df

	def predicates_freq(self):
		"""
		A function that returns all the predicates and their frequency
		"""
		query_string = str(PredicatesFreq(self.graph))
		result_df = self.client.execute_query(query_string)
		result_df.columns = ['predicate', 'freq']

		if return_format == 'df':
			return result_df




