__author__ = "Aisha Mohamed <ahmohamed@qf.org.qa>"


class SparqlQuery(object):
	"""
	A class for the sparql query
	"""
	def __init__(self, graph=None):
		super(SparqlQuery, self).__init__()
		if graph is not None:
			self.graph = ' FROM <'+ graph +'> '
		else:
			self.graph = ' '

	def __str__(self):
		pass


class NTriples(SparqlQuery):
	"""
	A class for the sparql query that returns the number of triples
	"""
	def __str__(self):
		return 'SELECT count(DISTINCT*)' + self.graph + 'WHERE { ?s ?p ?o}'


class NE2ETriples(SparqlQuery):
	"""
	A class for the sparql query that returns the number of triples
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT count(*)' + self.graph + \
			'WHERE {{ SELECT DISTINCT ?s ?p ?o WHERE { ?s ?p ?o {SELECT DISTINCT ?p' + self.graph+ \
			'WHERE { ?a ?p ?b . ?b rdf:type ?c}}}} UNION {SELECT DISTINCT ?s (rdf:type as ?p) ?o' + self.graph \
			+ 'WHERE {?s rdf:type ?o }}}'


class NE2LTriples(SparqlQuery):
	"""
	A class for the sparql query that returns the number of triples
	"""
	def __str__(self):
		return 'SELECT count(DISTINCT *)' + self.graph + 'WHERE { {SELECT DISTINCT ?s ?p ?o WHERE {?s ?p ?o . {SELECT DISTINCT ?p'+ self.graph + 'WHERE { ?a ?p ?b . FILTER isLiteral(?b)}}}}}'


class NRDFTTypeTriples(SparqlQuery):
	"""
	A class for the sparql query that returns the number of (?s rdf:type ?c) triples
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT count(*) WHERE { {SELECT DISTINCT ?s rdf:type ?o' + self.graph + \
			'WHERE {?s rdf:type ?o }}}'


class NEntities(SparqlQuery):
	"""
	A class for the sparql query that returns the number of entities
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT count(DISTINCT ?s)' \
			+ self.graph + 'WHERE {?s rdf:type ?c}'


class NPredicates(SparqlQuery):
	def __str__(self):
		return 'SELECT COUNT(DISTINCT ?p)' + self.graph + 'WHERE { ?s ?p ?o }'


class NRelations(SparqlQuery):
	"""
	A class for the sparql query that returns the number of relations
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT count(DISTINCT ?p)' + \
			self.graph + 'WHERE { {?s ?p ?o . ?o rdf:type ?c} UNION {SELECT (rdf:type as ?p) WHERE {}} }'


class NAttributes(SparqlQuery):
	"""
	A class for the sparql query that returns the number of attributes
	"""
	def __str__(self):
		return 'SELECT count(DISTINCT ?p)' + self.graph + 'WHERE { ?s ?p ?o . FILTER isLiteral(?o)}'


class NAttributeLiteralPairs(SparqlQuery):
	"""
	A class for the sparql query that returns the number of attr_literal_pairs
	"""
	def __str__(self):
		return 'SELECT COUNT (*) WHERE {SELECT DISTINCT ?p ?o' + self.graph + \
			'WHERE { ?s ?p ?o . FILTER isLiteral(?o)}}'


class Triples(SparqlQuery):
	"""
	A class for the sparql query that returns the triples
	"""
	def __str__(self):
		return 'SELECT DISTINCT ?s ?o ?p' + self.graph + 'WHERE { ?s ?p ?o}'


class E2ETriples(SparqlQuery):
	"""
	A class for the sparql query that returns the number of triples
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?s ?o ?p' + self.graph + \
			'WHERE {?s ?p ?o . {SELECT ?p WHERE { ?a ?p ?b . ?b rdf:type ?c}}}'


class RDFTTypeTriples(SparqlQuery):
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT (?s ?o rdf:type as ?p)' + self.graph + \
			'WHERE {?s rdf:type ?o }'


class E2LTriples(SparqlQuery):
	"""
	A class for the sparql query that returns the number of triples
	"""
	def __str__(self):
		return 'SELECT *' + self.graph + 'WHERE { ?s ?p ?o . {SELECT DISTINCT ?p' + \
			'WHERE { ?a ?p ?b . FILTER isLiteral(?b)}}}'


class Entities(SparqlQuery):
	"""
	A class for the sparql query that returns the entities
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?s' + \
			self.graph + 'WHERE {?s rdf:type ?c}'


class Relations(SparqlQuery):
	"""
	A class for the sparql query that returns the entity to entiity relations
	"""
	def __str__(self):
		return 'PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?p' + \
			self.graph + 'WHERE { {?s ?p ?o . ?o rdf:type ?c} UNION {SELECT (rdf:type as ?p) WHERE {}} } '


class Attributes(SparqlQuery):
	"""
	A class for the sparql query that returns the  attributes
	"""
	def __str__(self):
		return 'SELECT DISTINCT ?p' + self.graph + 'WHERE { ?s ?p ?o . FILTER isLiteral(?o)}'


class Predicates(SparqlQuery):
	"""
	A class for the sparql query that returns the predicates
	"""
	def __str__(self):
		return 'SELECT DISTINCT ?p' + self.graph + 'WHERE { ?s ?p ?o }'


class AttributeLiteralPairs(SparqlQuery):
	"""
	A class for the sparql query that returns the attr_literal_pairs
	"""
	def __str__(self):
		return 'SELECT DISTINCT ?p ?o' + self.graph + 'WHERE { ?s ?p ?o . FILTER isLiteral(?o)}'


class Subjects(SparqlQuery):
	"""
	A class for the sparql query that returns the subjects of a given predicate p.
	It returns all the subjects ?s that match the following pattern
		?s p ?o
	"""
	def __init__(self, graph, p):
		super(Subjects, self).__init__(graph)
		self.p = p

	def __str__(self):
		return 'SELECT DISTINCT ?s' + self.graph + 'WHERE { ?s <' + self.p + '> ?o }'


class Objects(SparqlQuery):
	"""
	A class for the sparql query that returns the objects of a given predicate p.
	It returns all the objects ?o that match the following pattern
		?s p ?o
	"""
	def __init__(self, graph, p):
		super(Objects, self).__init__(graph)
		self.p = p

	def __str__(self):
		return 'SELECT DISTINCT ?o' + self.graph + 'WHERE { ?s <' + self.p + '> ?o }'


class PredicatesFreq(SparqlQuery):
	"""
	A class for the sparql query that returns the predicates of a given graph.
	It returns all the predicates ?p that match the following pattern
		?s p ?o
	"""
	def __str__(self):
		return 'SELECT ?p COUNT(DISTINCT *)' + self.graph + 'WHERE { ?s ?p ?o } GROUP BY ?p'


class PTriples(SparqlQuery):
	def __init__(self, graph, p):
		super(PTriples, self).__init__(graph)
		self.p = p

	def __str__(self):
		return 'SELECT DISTINCT ?s ?o <'+ self.p + '>' + self.graph + 'WHERE { ?s <' + self.p +'> ?o }'

class NPTriples(SparqlQuery):
	def __init__(self, graph, p):
		super(NPTriples, self).__init__(graph)
		self.p = p

	def __str__(self):
		return 'SELECT COUNT(DISTINCT *)' + self.graph + 'WHERE { ?s <' + self.p +'> ?o }'
