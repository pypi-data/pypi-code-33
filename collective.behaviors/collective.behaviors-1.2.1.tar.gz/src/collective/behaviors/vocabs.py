from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import provider
from .util import get_registry_entry


# @provider(IContextSourceBinder)
def allowed_containers_as_creator_vocab(context=None):
    allowed_containers = get_registry_entry(
        "collective.behaviors.containers_as_creators"
    )
    return SimpleVocabulary.fromValues(allowed_containers)
