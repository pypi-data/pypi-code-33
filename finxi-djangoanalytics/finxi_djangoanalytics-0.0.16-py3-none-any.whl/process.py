import logging
from .models import User, RawHit


def default_process(hit_dict):
    user = User.objects.get(cid=hit_dict['cid'])
    user.update_custom_variables(hit_dict)
    hit = RawHit.objects.create(hit_dict, user)
    user.update_last_hit(hit)
    return user, hit

def process_hit(hit_dict, user_model, hit_model):
    user = user_model.objects.auth_user(hit_dict)
    user.update_custom_variables(hit_dict)
    hit = hit_model.objects.create(hit_dict, user)
    user.update_last_hit(hit)
    return user, hit
