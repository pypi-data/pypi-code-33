import string
import random
from django.db import models
from django.db.models import Min
from django.conf import settings
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField


GA_VARIABLES = getattr(settings, "GA_CUSTOM_VARIABLES", None)


def get_variables(hit_dict, variable_scope, variable_type):
    not_found = {'scope': None, 'type': None}
    return {key: value for key, value in hit_dict.items()
            if GA_VARIABLES.get(key, not_found)['scope'] == variable_scope and
            GA_VARIABLES.get(key, not_found)['type'] == variable_type}


def random_id(size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


class CustomId(models.Model):
    id = models.TextField(primary_key=True)

    class Meta:
        abstract = True


class ImpressionableManager(models.Manager):
    def auth(self, hit_dict, id_field):
        try:
            impressionable = self.get(id=hit_dict[id_field])
        except self.model.DoesNotExist:
            impressionable = self.new(hit_dict, id_field)
        return impressionable

    def attribution(self, hit_dict):
        return {'session_source': hit_dict.get('cs', ''), 
                'session_medium':  hit_dict.get('cm', ''),
                'campaign_name': hit_dict.get('cn', ''), 
                'campaign_keyword': hit_dict.get('ck', '')}

    def new(self, hit_dict, id_field):
        attribution = self.attribution(hit_dict)
        impressionable = self.model(id=hit_dict[id_field],
                                    session_attribution=attribution)
        impressionable.save()
        return impressionable


class Impressionable(models.Model):
    objects = ImpressionableManager()

    session_attribution = JSONField(default=dict)

    class Meta:
        abstract = True


class Attributionable(models.Model):
    def get_attribution_path(self, HitModel, field_in_hit):
        visits = HitModel.objects.filter(**{field_in_hit: self.id})\
            .values('session_id', 'session_source', 'session_medium',
                    'campaign_name', 'campaign_keyword')\
            .annotate(time=Min('created'))
        attribution = {str(visit.pop('time')): visit for visit in visits}
        return attribution

    def lnd(self, path_json):
        path_list = list(path_json.items())
        if len(path_list) == 0:
            return {}
        path_list.sort(key=lambda x: x[0], reverse=True)
        for (time, session) in path_list:
            if session['session_source'] != 'direct':
                return session
        return path_list[0][1]

    attribution_path = JSONField(default=dict)
    lnd_attribution = JSONField(default=dict)

    class Meta:
        abstract = True


class TrackableManager(ImpressionableManager):
    def auth(self, hit_dict, id_field):
        trackable = super().auth(hit_dict, id_field)
        trackable.update_custom_variables(hit_dict)
        return trackable


class Trackable(TimeStampedModel, CustomId, Attributionable, Impressionable):
    objects = TrackableManager()

    def update_custom_variables(self, hit_dict):
        new_dimensions = get_variables(hit_dict, 'user', 'dimension')
        new_metrics = get_variables(hit_dict, 'user', 'metric')
        self.dimensions.update(new_dimensions or {})
        self.metrics.update(new_metrics or {})
        self.save()
        return self

    def get_last_hit(self, HitModel):
        try:
            return HitModel.objects.get(id=self.last_hit)
        except Exception:
            return None

    def update_last_hit(self, hit):
        self.last_hit = hit.id
        self.save()
        return self

    def update_known_users(self, hit):
        if hit.user_id != '':
            known_users = self.known_users
            if hit.user_id not in known_users.keys():
                self.nr_users = self.nr_users + 1 \
                    if self.nr_users is not None else 1
            known_users[hit.user_id] = str(hit.created)
            self.known_users = known_users
            self.save()
        return self

    metrics = JSONField(default=dict)
    dimensions = JSONField(default=dict)
    last_hit = models.TextField(null=True)
    known_users = JSONField(default=dict)
    nr_users = models.SmallIntegerField(null=True)

    class Meta:
        abstract = True


class IndentifiableManager(ImpressionableManager):
    def user_auth(self, hit_dict, id_field, trackable, HitModel, field_in_hit):
        try:
            user = self.get(id=hit_dict[id_field])
        except KeyError:
            return None
        except self.model.DoesNotExist:
            user = self.new(hit_dict, id_field, trackable, HitModel,
                            field_in_hit)
        return user

    def new(self, hit_dict, id_field, trackable, HitModel, field_in_hit):
        user = super().new(hit_dict, id_field)
        user.original_cid = trackable.id
        att_path = trackable.get_attribution_path(HitModel, field_in_hit)
        if att_path == {}:
            att_path = {str(trackable.created): trackable.session_attribution}
        user.attribution_path = att_path
        user.lnd_attribution = user.lnd(att_path)
        user.save()
        return user


class Indentifiable(TimeStampedModel, CustomId, Attributionable,
                    Impressionable):
    objects = IndentifiableManager()

    def update_known_cids(self, hit):
        if hit.user_id == self.id:
            known_cids = self.known_cids
            if hit.cid not in known_cids.keys():
                self.nr_cids = self.nr_cids + 1 \
                    if self.nr_cids is not None else 1
            known_cids[hit.cid] = str(hit.created)
            self.known_cids = known_cids
            self.save()
        return self

    def get_attribution_path(self, HitModel, field_in_hit):
        identifiable_path = super().get_attribution_path(HitModel,
                                                         field_in_hit)
        original_cid_path = self.attribution_path
        return {**original_cid_path, **identifiable_path}

    original_cid = models.TextField(blank=True)
    known_cids = JSONField(default=dict)
    nr_cids = models.SmallIntegerField(null=True)

    class Meta:
        abstract = True
