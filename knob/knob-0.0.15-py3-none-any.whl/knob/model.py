# -*- coding:utf-8 -*-

import six
from django.db import models
from django.contrib.auth import get_user_model


def update_model(obj, info, fields=None):
    """
    Updates an object of Django model instance with given info, optionally limited to certain fields only.
    :param obj: a Django model instance
    :param info: a dict
    :param fields: optional, only update these fields.
    :return: updated obj (saved)
    """
    update_fields = set()
    for key, val in six.iteritems(info):
        if fields is None or key in fields:
            setattr(obj, key, val)
        update_fields.add(key)

    if update_fields:
        obj.save(update_fields=list(update_fields))

    return obj


def get_model_class(model):
    """
    Deduct the model class from given input.
    :param model: may be one of the following format:
        * a '<app>.<model>' string
        * 'AUTH_USER_MODEL'
        * a django model instance,
        * a model class
    :return: django model class
    """
    # Special cases
    if model is None:
        return None

    if model == 'AUTH_USER_MODEL':
        return get_user_model()

    from django.contrib.contenttypes.models import ContentType
    if isinstance(model, six.string_types):
        if '.' in model:
            app_label, model_name = model.split('.')
            model_name = model_name.lower()
            return ContentType.objects.get(app_label=app_label, model=model_name).model_class()
        else:
            model_name = model.lower()
            return ContentType.objects.get(model=model_name).model_class()
    elif isinstance(model, six.class_types) and issubclass(model, models.Model):
        return model
    elif isinstance(model, models.Model):
        return model.__class__
    else:
        raise ValueError(u"Not a valid model representation: {}".format(repr(model)))
