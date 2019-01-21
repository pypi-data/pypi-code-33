import pandas as pd
import json
import csv


from .queries import *
from .rdfloader import RDFGraphDataset

__author__ = "Aisha Mohamed <ahmohamed@qf.org.qa>"


class SmartRDFGraphDataset(RDFGraphDataset):
	"""
	A class for loading and processing RDF datasets for relational learning models
	It provides some convenience functions for accessing a knowldge graph from a sparql endpoint
	"""
	def __init__(self, sparql_endpoint, graph_name=None):
		super(SmartRDFGraphDataset, self).__init__(sparql_endpoint, graph_name)

	def entity2entity_triples(self, return_format='list', entity2idx=None, relation2idx=None,
		return_dict = False, output_dir=None):
		"""
		A function that returns all the entity2entity triples in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param relation2idx: a dictionary mapping each entity in the graph to an index from 0 to n_relations-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
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

		results_df = pd.DataFrame(columns=['subject', 'object', 'predicate'])
		for relation in relation2idx:
			query_string = str(PTriples(self.graph, relation))
			result_df = self.client.execute_query(query_string)
			result_df.columns = ['subject', 'object', 'predicate']
			result_df['subject'] = result_df['subject'].map(entity2idx)
			result_df['object'] = result_df['object'].map(entity2idx)
			result_df['predicate'] = result_df['predicate'].map(relation2idx)
			results_df = pd.merge(results_df, result_df, how='outer')
		
		if output_dir is not None:
			results_df.to_csv(output_dir+"/entity2entity_triples.csv", index=False)
			with open(output_dir+"/relation2idx.json", 'w') as fp:
				json.dump(relation2idx, fp)
			with open(output_dir+"/entity2idx.json", 'w') as fp:
				json.dump(entity2idx, fp)

		if return_format == 'list':
			if return_dict:
				return results_df.values.tolist(), entity2idx, relation2idx
			return results_df.values.tolist() 
		elif return_format == 'df':
			if return_dict:
				return results_df, entity2idx, relation2idx
			return results_df

	def entity2literal_triples(self, entity2idx=None, attribute_literal_pair2idx=None, return_format='list',
							   return_dict = False, output_dir=None):
		"""
		A function that returns all the entity2literal triples in the specified graph as indices rather than URIs
		:param entity2idx: a dictionary mapping each entity in the graph to an index from 0 to n_entities-1
		:param attribute_literal_pair2idx: a dictionary mapping each entity in the graph to an index from 0 to
		n_relations-1
		:param return_format: one of ['list', 'df']
		:return: the triples in the graph in the specified format
		"""
		if entity2idx is None:
			if self.entity2idx is None:
				entity2idx = self.entities('dict')
			else:
				entity2idx = self.entity2idx
		# find the dictionary mapping each relation to its index
		if attribute_literal_pair2idx is None:
			if self.attribute_literal_pair2idx is None:
				attribute_literal_pair2idx = self.attr_literal_pairs('dict')
			else:
				attribute_literal_pair2idx = self.attribute_literal_pair2idx

		attributes = self.attributes('dict')

		results_df = pd.DataFrame(columns=['subject', 'attribute_literal_pair'])
		for attribute in attributes:
			query_string = str(PTriples(self.graph, attribute))
			result_df = self.client.execute_query(query_string)
			result_df.columns = ['subject', 'object', 'predicate']
			result_df["attribute_literal_pair"] = result_df["predicate"] + result_df["object"]
			result_df = result_df.drop(columns=['object', 'predicate'])
			result_df['subject'] = result_df['subject'].map(entity2idx)
			result_df['attribute_literal_pair'] = result_df['attribute_literal_pair'].map(attribute_literal_pair2idx)
			results_df = pd.merge(results_df, result_df, how='outer')
		
		if output_dir is not None:
			results_df.to_csv(output_dir+"/entity2literal_triples.csv", index=False)
			with open(output_dir+"/attribute_literal_pair2idx.json", 'w') as fp:
				json.dump(attribute_literal_pair2idx, fp)
			with open(output_dir+"/entity2idx.json", 'w') as fp:
				json.dump(entity2idx, fp)

		if return_format == 'list':
			if return_dict:
				return results_df.values.tolist(), entity2idx, attribute_literal_pair2idx
			return results_df.values.tolist() 
		elif return_format == 'df':
			if return_dict:
				return results_df, entity2idx, attribute_literal_pair2idx
			return results_df


	def subjects(self, p, entity2idx=None, return_format='list', output_dir=None):
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
		result_df['subject'] = result_df['subject'].map(entity2idx)

		if output_dir is not None:
			with open(output_dir+"{}_subjects.csv".format(p), "wb") as f:
				writer = csv.writer(f)
				writer.writerows(result_df.values.tolist())

		if return_format == 'list':
			return result_df['subject'].values
		elif return_format == 'df':
			return result_df

	def objects(self, p, entity2idx=None, return_format='list', output_dir=None):
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
		result_df['object'] = result_df['object'].map(entity2idx)

		if output_dir is not None:
			with open(output_dir+"{}_objects.csv".format(p), "wb") as f:
				writer = csv.writer(f)
				writer.writerows(result_df.values.tolist())
		if return_format == 'list':
			return result_df['object'].values
		elif return_format == 'df':
			return result_df

	def predicates_freq(self):
		predicates = self.predicates('list')
		print("predicates are {}".format(predicates))

		results_df = pd.DataFrame(columns=['predicate', 'frequency'])
		for predicate in predicates:
			query_string = str(NPTriples(self.graph, predicate))
			print(query_string)
			result = self.client.execute_query(query_string).values.tolist()[0][0]
			print(result)
			results_df = results_df.append({'predicate' : predicate , 'frequency' : result} , ignore_index=True)
		return results_df
