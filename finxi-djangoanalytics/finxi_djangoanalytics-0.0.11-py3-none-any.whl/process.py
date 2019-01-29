from .models import User, RawHit
import logging


def process_hit(hit_dict):
    user = User.objects.get(cid=hit_dict['cid'])
    user.update_custom_variables(hit_dict)
    hit = RawHit.objects.create(hit_dict, user)
    user.update_last_hit(hit)
    return user, hit
