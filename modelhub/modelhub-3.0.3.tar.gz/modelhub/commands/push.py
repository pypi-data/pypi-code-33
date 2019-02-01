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
        model = Model.get_local(model_name, fallback_to_remote=False)
        versions = model.manifest.versions
        model_version = None
        if version is None:
            model_version = versions[-1]
        elif version:
            for v in versions:
                if version == v.seq:
                    model_version = v
                    break
        if model_version:
            model.push(model_version)
        else:
            print("could not find [ %s@%d ] in local." % (model_name, version))