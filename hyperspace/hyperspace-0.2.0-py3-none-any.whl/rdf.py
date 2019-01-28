from hyperspace.affordances import FilterableList, Link, Page, Query
from rdflib import Namespace, Graph, URIRef
from uritemplate import URITemplate, expand


HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')


class RDFPage(Page):

    format = None

    def __init__(self, response):
        self.data = Graph()
        self.links = FilterableList()
        self.queries = FilterableList(base_url=response.url)
        super(RDFPage, self).__init__(response)

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text, format=self.format, publicID=self.url)

    def extract_links(self):
        for p, o in self.data.predicate_objects(URIRef(self.url)):
            if isinstance(o, URIRef):
                link = Link(p.toPython(), o.toPython())
                self.links.append(link)

    def extract_queries(self):
        rows = self.data.query('''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX schema: <http://schema.org/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        SELECT ?rel ?template
        WHERE {
            ?url ?rel ?action .
            ?action rdf:type hydra:IriTemplate .
            ?action hydra:template ?template .
        }
        ''')

        for rel, template in rows:
            self.queries.append(Query(str(rel), str(template), base_url=self.response.url))
