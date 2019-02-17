"""
The rdflib_django implementation uses Django models to store its triples.

The underlying models are Resource centric, because rdflib-django is intended
to be used for publishing resources.
"""  # noqa: E501
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from rdflib_django import fields


class Store(models.Model):
    """
    Models a store of a named graph.
    """

    identifier = models.CharField(
        verbose_name=_("Identifier"), unique=True, max_length=255,
        db_index=True
    )

    class Meta:
        verbose_name = _("Store")

    def __str__(self):
        return "{}-{}".format(self.identifier, "identifier")


class NamedGraph(models.Model):
    """
    Models a context which represents a named graph.
    """

    identifier = fields.URIField(
        verbose_name=_("Identifier"), db_index=True
    )

    store = models.ForeignKey(
        Store, verbose_name=_("Store"), on_delete=models.CASCADE,
        db_index=True
    )

    class Meta:
        verbose_name = _("named graph")
        verbose_name_plural = _("named graphs")
        unique_together = [
            ("identifier", "store"),
        ]

    def __str__(self):
        return "{}-{}".format(self.identifier, "identifier")


class NamespaceModel(models.Model):
    """
    A namespace definition.

    In essence, a namespace consists of a prefix and a URI. However, the namespaces in rdflib_django
    also have an extra field called '`fixed`' - this is used to mark namespaces that cannot be
    remapped such as ``xsd``, ``xml``, ``rdf`` and ``rdfs``.
    """  # noqa: E501

    prefix = models.CharField(
        max_length=50, verbose_name=_("Prefix"), db_index=True
    )
    uri = models.CharField(
        max_length=500, verbose_name=_("URI"), db_index=True
    )
    store = models.ForeignKey(
        Store, verbose_name=_("Store"), on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        verbose_name = _("namespace")
        verbose_name_plural = _("namespaces")
        unique_together = [
            ("prefix", "store"),
            ("uri", "store"),
        ]

    def __str__(self):
        return "@prefix {}: <{}>".format(self.prefix, self.uri)


class URIStatement(models.Model):
    """
    Statement where the object is a URI.
    """

    id = models.UUIDField("ID", default=uuid.uuid4, primary_key=True)
    subject = fields.URIField(verbose_name=_("Subject"), db_index=True)
    predicate = fields.URIField(_("Predicate"), db_index=True)
    object = fields.URIField(_("Object"), db_index=True)
    context = models.ForeignKey(
        NamedGraph, verbose_name=_("Context"),
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('subject', 'predicate', 'object', 'context')

    def __str__(self):
        return "{}, {}".format(self.as_triple(), self.context.identifier)

    def as_triple(self):
        """
        Converts this predicate to a triple.
        """
        return self.subject, self.predicate, self.object


class LiteralStatement(models.Model):
    """
    Statement where the object is a literal.
    """

    id = models.UUIDField("ID", default=uuid.uuid4, primary_key=True)
    subject = fields.URIField(verbose_name=_("Subject"), db_index=True)
    predicate = fields.URIField(_("Predicate"), db_index=True)
    object = fields.LiteralField(_("Object"))
    context = models.ForeignKey(
        NamedGraph, verbose_name=_("Context"),
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('subject', 'predicate', 'object', 'context')

    def __str__(self):
        return "{}, {}".format(self.as_triple(), self.context.identifier)

    def as_triple(self):
        """
        Converts this predicate to a triple.
        """
        return self.subject, self.predicate, self.object
