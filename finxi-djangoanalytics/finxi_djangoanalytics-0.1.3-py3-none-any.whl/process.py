from .models import RawHit, RawCid, RawUser


def default_vision(hit_dict):
    return RawHit.objects.create(hit_dict, RawCid, RawUser)


def populate_model(json, model_manganer):
    model_instance = model_manganer.model()
    for field in model_instance._meta.fields:
        if not field.primary_key and field.name in json:
            setattr(model_instance, field.name, json[field.name])
    return model_instance


def model_to_json(model_instance):
    model_json = {}
    for field in model_instance._meta.fields:
            model_json[field.name] = str(getattr(model_instance, field.attname))
    return model_json
