# -*- coding: utf-8 -*

from modelhub.core.models import Model, ModelVersion
from .base import BaseCommand, argument, option, types, register


@register("push")
class Command(BaseCommand):
    """
    push the existed model(you did checkout it before) to the remote
    default push the latest version in local
    """
    arguments = [
        argument("model_name", type=types.STRING)
    ]

    def run(self, model_name):
        version = None
        try:
            model_name, version = Model.split_name_version(model_name)
        except:
            print("invalid model name and version %s" % model_name)
        model = Model.get_local(model_name)
        versions = model.manifest.versions
        if version and version > 0 and version <=len(versions):
            model_version = versions[version-1]
        else:
            model_version = versions[-1]
        model.push(model_version)