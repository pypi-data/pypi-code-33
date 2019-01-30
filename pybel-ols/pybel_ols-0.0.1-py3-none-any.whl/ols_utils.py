# -*- coding: utf-8 -*-

"""PyBEL-OLS Reference."""

import json
import os
from collections import defaultdict
from itertools import repeat
from typing import Iterable, List, Optional, TextIO, Tuple, Type

from bel_resources import write_annotation, write_namespace
from ols_client import BASE_URL, OlsClient

from pybel import BELGraph
from pybel.constants import NAMESPACE_DOMAIN_TYPES, belns_encodings, rev_abundance_labels
from pybel.dsl import BaseEntity

__all__ = [
    'OlsOntology',
    'OlsNamespaceOntology',
    'OlsAnnotationOntology',
    'OlsConstrainedOntology',
    'OlsConstrainedNamespaceOntology',
    'OlsConstrainedAnnotationOntology',
    'BASE_URL',
]

function_to_encoding = defaultdict(list)
for enc, functions in belns_encodings.items():
    for fn in functions:
        function_to_encoding[fn].append(enc)


class OlsOntology(object):
    """Wraps the functions needed to use the OLS to generate and deploy BEL namespaces."""

    def __init__(self, ontology: str, *, ols_base: Optional[str] = None, auth: Optional[Tuple[str, str]] = None):
        """Build a wrapper around an OLS ontology.

        :param ontology: The name of the ontology. Ex: ``uberon``, ``go``, etc.
        :param ols_base: An optional, custom OLS base url
        :param auth: A pair of (str username, str password) to give to the auth keyword of the constructor of
         :class:`artifactory.ArtifactoryPath`. Looks up from environment by default.
        """
        self.ontology = ontology
        self.ols_client = OlsClient(ols_base=ols_base)

        if auth is not None:
            self.auth = auth
        elif 'ARTY_USERNAME' in os.environ and 'ARTY_PASSWORD' in os.environ:
            self.auth = (os.environ['ARTY_USERNAME'], os.environ['ARTY_PASSWORD'])
        else:
            self.auth = None

        self.metadata = self.ols_client.get_ontology(self.ontology)

        if self.metadata['status'] == 404:
            raise ValueError('Error from OLS:\n{}'.format(json.dumps(self.metadata, indent=2)))

    @property
    def title(self) -> str:
        """Return the ontology's full name."""
        return self.metadata['config']['title']

    @property
    def preferred_prefix(self) -> str:
        """Return the ontology's preferred prefix, usually uppercase."""
        return self.metadata['config']['preferredPrefix']

    @property
    def description(self) -> str:
        """Return a description of the ontology."""
        return self.metadata['config']['description']

    @property
    def version(self) -> str:
        """Return the version of the ontology."""
        return self.metadata['config']['version']

    @property
    def version_iri(self) -> str:
        """Return the IRI of this version of the ontology."""
        return self.metadata['config']['versionIri']

    def _get_values(self) -> Iterable[str]:
        """Iterate over the labels for this ontology."""
        return self.ols_client.iter_labels(self.ontology)

    def _get_hierarchy(self) -> Iterable[Tuple[str, str]]:
        """Iterate over the hierarchy for this ontology."""
        return self.ols_client.iter_hierarchy(self.ontology)


class OlsNamespaceOntology(OlsOntology):
    """Wraps the functions needed to use the OLS to generate and deploy BEL namespaces."""

    def __init__(self, ontology, namespace_domain, *, bel_function=None, encoding=None, ols_base=None, auth=None):
        """Build a wrapper around an ontology with BEL namespace utilities.

        :param str ontology: The name of the ontology. Ex: ``uberon``, ``go``, etc.
        :param str namespace_domain: One of: :data:`pybel.constants.NAMESPACE_DOMAIN_BIOPROCESS`,
                            :data:`pybel.constants.NAMESPACE_DOMAIN_CHEMICAL`,
                            :data:`pybel.constants.NAMESPACE_DOMAIN_GENE`, or
                            :data:`pybel.constants.NAMESPACE_DOMAIN_OTHER`
        :param str bel_function: The BEL function of elements of this ontology. One of
                                :data:`pybel.constants.ABUNDANCE`, etc.
        :param str ols_base: An optional, custom OLS base url
        :param tuple[str,str] auth: A pair of (str username, str password) to give to the auth keyword of the
                                    constructor of :class:`artifactory.ArtifactoryPath`. Defaults to the result of
                                    :func:`pybel_tools.resources.get_arty_auth`.
        """
        super(OlsNamespaceOntology, self).__init__(ontology=ontology, ols_base=ols_base, auth=auth)

        if bel_function is None and encoding is None:
            raise ValueError('either bel_function or encoding must be specified')

        if namespace_domain not in NAMESPACE_DOMAIN_TYPES:
            raise ValueError('{} is not valid. Should be one of {}'.format(namespace_domain, NAMESPACE_DOMAIN_TYPES))

        self.namespace_domain = namespace_domain
        self._bel_function = bel_function
        self._encoding = encoding

    @property
    def bel_function(self) -> str:
        """Return the BEL function for this ontology."""
        return rev_abundance_labels[self._bel_function]

    @property
    def encodings(self) -> List[str]:
        """Return the encodings that should be used when outputting this ontology as a BEL namespace."""
        if self._encoding:
            return self._encoding

        return function_to_encoding[self._bel_function]

    def write_namespace(self, file: Optional[TextIO] = None):
        """Write this ontology as a BEL namespace."""
        write_namespace(
            namespace_name=self.title,
            namespace_keyword=self.preferred_prefix,
            namespace_domain=self.namespace_domain,
            namespace_description=self.description,
            namespace_version=self.version,
            citation_name=self.title,
            citation_url=self.version_iri,
            author_name='Charles Tapley Hoyt',
            author_contact='charles.hoyt@scai.fraunhofer.de',
            author_copyright='Creative Commons by 4.0',
            values=zip(self._get_values(), repeat(''.join(self.encodings))),
            file=file
        )

    def _get_dsl_func(self) -> Type[BaseEntity]:
        """Get the PyBEL DSL type."""
        raise NotImplementedError

    def _get_node(self, name: Optional[str] = None, identifier: Optional[str] = None) -> BaseEntity:
        return self._get_dsl_func()(self.preferred_prefix, name=name, identifier=identifier)

    def _get_hierarchy_graph(self) -> BELGraph:
        from pybel_artifactory import get_namespace_latest

        graph = BELGraph(
            name=self.title,
            description=self.description,
            authors='Charles Tapley Hoyt',
            contact='charles.hoyt@scai.fraunhofer.de',
            version=self.version,
        )

        # TODO need better way
        graph.namespace_url[self.preferred_prefix] = get_namespace_latest(self.ontology)

        for parent, child in self._get_hierarchy():
            graph.add_is_a(self._get_node(name=child), self._get_node(name=parent))

        return graph

    def write_namespace_hierarchy(self, file: Optional[TextIO] = None):
        """Serialize the hierarchy in this ontology as BEL."""
        graph = self._get_hierarchy_graph()
        graph.serialize('bel', file=file)


class OlsAnnotationOntology(OlsOntology):
    """Wraps the functions needed to use the OLS to generate and deploy BEL annotations."""

    def write_annotation(self, file: Optional[TextIO] = None) -> None:
        """Serialize this ontology as a BEL annotation."""
        write_annotation(
            keyword=self.preferred_prefix,
            values={x: '' for x in self._get_values()},
            citation_name=self.title,
            description=self.description,
            version=self.version,
            author_name='Charles Tapley Hoyt',
            author_contact='charles.hoyt@scai.fraunhofer.de',
            author_copyright='Creative Commons by 4.0',
            file=file
        )


class OlsConstrainedOntology(OlsOntology):
    """Specifies that only the hierarchy under a certain term should be followed."""

    def __init__(self, ontology: str, base_term_iri: str, *, ols_base: Optional[str] = None,
                 auth: Optional[Tuple[str, str]] = None):
        """Build a wrapper around an ontology that is constrained to descendants of a specific term.

        :param str ontology: The name of the ontology. Ex: ``uberon``, ``go``, etc.
        :param str namespace_domain: One of: :data:`pybel.constants.NAMESPACE_DOMAIN_BIOPROCESS`,
                            :data:`pybel.constants.NAMESPACE_DOMAIN_CHEMICAL`,
                            :data:`pybel.constants.NAMESPACE_DOMAIN_GENE`, or
                            :data:`pybel.constants.NAMESPACE_DOMAIN_OTHER`
        :param str bel_function: The BEL function of elements of this ontology
        :param str ols_base: An optional, custom OLS base url
        :param tuple[str,str] auth: A pair of (str username, str password) to give to the auth keyword of the
                                    constructor of :class:`artifactory.ArtifactoryPath`. Defaults to the result of
                                    :func:`pybel_tools.resources.get_arty_auth`.
        """
        super(OlsConstrainedOntology, self).__init__(
            ontology=ontology,
            ols_base=ols_base,
            auth=auth
        )

        self.base_term_iri = base_term_iri

        self._labels = None
        self._hierarchy = None

    def _get_values(self):
        return self.ols_client.iter_descendants_labels(self.ontology, self.base_term_iri)

    def _get_hierarchy(self):
        raise NotImplementedError


class OlsConstrainedNamespaceOntology(OlsConstrainedOntology, OlsNamespaceOntology):
    """Wraps the functions needed to use the OLS to generate and deploy constrained BEL namespaces."""


class OlsConstrainedAnnotationOntology(OlsConstrainedOntology, OlsAnnotationOntology):
    """Wraps the functions needed to use the OLS to generate and deploy constrained BEL annotations."""
