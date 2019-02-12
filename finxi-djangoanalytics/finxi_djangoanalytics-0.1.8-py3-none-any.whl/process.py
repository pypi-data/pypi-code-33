from .models import RawHit, User, Cid, get_variables


class Analytics():
    def __init__(self, trackable_id):
            self.trackable = Cid.objects.get(id=trackable_id)
            self.UserModel = User

    def vision(self, hit_dict, HitModel):
            cid, user, hit = HitModel.objects.create(hit_dict, self.trackable,
                                           self.UserModel)
            return hit

    def default(self, hit_dict):
            return RawHit.objects.create(hit_dict, self.trackable,
                                         self.UserModel)


def populate_model(json, model_manganer):
    model_instance = model_manganer.model()
    for field in model_instance._meta.fields:
        if field.name in json:
            setattr(model_instance, field.name, json[field.name])
    return model_instance


def model_to_json(model_instance):
    model_json = {}
    for field in model_instance._meta.fields:
            model_json[field.name] = str(getattr(model_instance, field.attname))
    return model_json
