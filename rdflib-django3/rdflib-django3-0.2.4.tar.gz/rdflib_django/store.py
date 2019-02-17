"""
Essential implementation of the Store interface defined by RDF lib.
"""
from django.db.models import Q
import rdflib
from rdflib.store import VALID_STORE
from rdflib.term import Literal, Identifier
from rdflib_django import models


DEFAULT_STORE = "Default Store"


def _get_query_sets_for_object(o):
    """
    Determines the correct query set based on the object.

    If the object is a literal, it will return a query set over LiteralStatements.
    If the object is a URIRef or BNode, it will return a query set over Statements.
    If the object is unknown, it will return both the LiteralStatement and Statement query sets.

    This method always returns a list of size at least one.
    """  # noqa: E501
    if o:
        if isinstance(o, Literal):
            query_sets = [models.LiteralStatement.objects]
        else:
            query_sets = [models.URIStatement.objects]
    else:
        query_sets = [
            models.URIStatement.objects,
            models.LiteralStatement.objects
        ]
    return query_sets


class DjangoStore(rdflib.store.Store):
    """
    RDFlib Store implementation the uses Django Models for storage and retrieval.

    >>> g = rdflib.Graph('Django')

    The implementation is context aware, and uses Django transactions.

    >>> g.store.context_aware
    True
    >>> g.store.transaction_aware
    False

    The implementation does not support formula's.

    >>> g.store.formula_aware
    False

    The implementation provides a single store with the identifier DEFAULT_STORE. This store
    is always present and needs not be opened.

    >>> g.store.identifier
    'Default Store'

    Using other stores is allowed

    >>> g = DjangoStore(identifier='HelloWorld')


    """  # noqa: E501

    context_aware = True
    formula_aware = False
    transaction_aware = False

    def __init__(self, configuration=None, identifier=DEFAULT_STORE):
        self.identifier = identifier
        self.store = models.Store.objects.get_or_create(
            identifier=identifier
        )[0]
        super(DjangoStore, self).__init__(configuration, identifier)
        self.open()

    def _get_named_graph(self, context):
        """
        Returns the named graph for this context.
        """
        if context is None:
            return None
        return models.NamedGraph.objects.get_or_create(
            identifier=context.identifier, store=self.store
        )[0]

    def open(self, configuration=None, create=False):
        """
        Opens the underlying store. This is only necessary when opening
        a store with another identifier than the default identifier.

        >>> g = rdflib.Graph('Django')
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        """  # noqa: E501
        return VALID_STORE

    def destroy(self, configuration=None):
        """
        Completely destroys a store and all the contexts and triples in the store.

        >>> store = DjangoStore()
        >>> g = rdflib.Graph(store=store)
        >>> g.open(configuration=None, create=True) == rdflib.store.VALID_STORE
        True
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        >>> g.destroy(configuration=None)
        >>> g.open(configuration=None, create=False) == rdflib.store.VALID_STORE
        True
        """  # noqa: E501
        models.Store.objects.filter(identifier=self.identifier).delete()

    def add(self, triple, context, quoted=False):
        """
        Adds a triple to the store.

        >>> from rdflib.term import URIRef
        >>> from rdflib.namespace import RDF

        >>> subject = URIRef('http://zoowizard.org/resource/Artis')
        >>> object = URIRef('http://schema.org/Zoo')
        >>> g = rdflib.Graph('Django', identifier="foo")
        >>> g.add((subject, RDF.type, object))
        >>> len(g)
        1

        """
        s, p, o = triple
        assert isinstance(s, Identifier)
        assert isinstance(p, Identifier)
        assert isinstance(o, Identifier)
        assert not quoted

        named_graph = self._get_named_graph(context)

        query_set = _get_query_sets_for_object(o)[0]
        query_set.get_or_create(
            subject=s,
            predicate=p,
            object=o,
            context=named_graph,
            )

    def remove(self, triple, context=None):
        """
        Removes a triple from the store.
        """
        s, p, o = triple
        named_graph = self._get_named_graph(context)
        query_sets = _get_query_sets_for_object(o)

        filter_parameters = dict()
        if named_graph is not None:
            filter_parameters['context_id'] = named_graph.id
        if s:
            filter_parameters['subject'] = s
        if p:
            filter_parameters['predicate'] = p
        if o:
            filter_parameters['object'] = o

        query_sets = [qs.filter(**filter_parameters) for qs in query_sets]

        for qs in query_sets:
            qs.delete()

    def triples(self, triple, context=None):
        """
        Returns all triples in the current store.
        """
        s, p, o = triple
        named_graph = self._get_named_graph(context)
        query_sets = _get_query_sets_for_object(o)

        filter_parameters = dict()
        if named_graph is not None:
            filter_parameters['context_id'] = named_graph.id
        if s:
            filter_parameters['subject'] = s
        if p:
            filter_parameters['predicate'] = p
        if o:
            filter_parameters['object'] = o

        query_sets = [qs.filter(**filter_parameters) for qs in query_sets]

        for qs in query_sets:
            for statement in qs:
                triple = statement.as_triple()
                yield triple, context

    def __len__(self, context=None):
        """
        Returns the number of statements in this Graph.
        """
        named_graph = self._get_named_graph(context)
        if named_graph is not None:
            return (
                models.LiteralStatement.objects.filter(
                    context_id=named_graph.id
                ).count() +
                models.URIStatement.objects.filter(
                    context_id=named_graph.id
                ).count()
            )
        else:
            return (
                models.URIStatement.objects.values(
                    'subject', 'predicate', 'object'
                ).distinct().count() +
                models.LiteralStatement.objects.values(
                    'subject', 'predicate', 'object'
                ).distinct().count())

    ####################
    # CONTEXT MANAGEMENT

    def contexts(self, triple=None):
        return models.NamedGraph.objects.filter(store=self.store).values_list(
            "identifier", flat=True
        )

    ######################
    # NAMESPACE MANAGEMENT

    def bind(self, prefix, namespace):
        # is fixed
        if models.NamespaceModel.objects.filter(
            Q(uri=namespace) | Q(prefix=prefix),
            store__isnull=True
        ).exists():
            return
        assert(self.store is not None)
        models.NamespaceModel.objects.filter(
            Q(uri=namespace) | Q(prefix=prefix),
            store=self.store
        ).delete()
        models.NamespaceModel.objects.create(
            prefix=prefix, uri=namespace, store=self.store
        )

    def prefix(self, namespace):
        try:
            ns = models.NamespaceModel.objects.get(
                Q(store=self.store) | Q(store=None),
                uri=namespace
            )
            return ns.prefix
        except models.NamespaceModel.DoesNotExist:
            return None

    def namespace(self, prefix):
        try:
            ns = models.NamespaceModel.objects.get(
                Q(store=self.store) | Q(store=None),
                prefix=prefix
            )
            return ns.uri
        except models.NamespaceModel.DoesNotExist:
            return None

    def namespaces(self):
        return models.NamespaceModel.objects.filter(
            Q(store=self.store) | Q(store=None)
        ).values_list(
            "prefix", "uri"
        )
