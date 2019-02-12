import pytz
import logging
from django.db import transaction
from datetime import datetime, timedelta
from djangoanalytics.behaviors.agents import Attributionable, \
    TimeStampedModel, random_id, get_variables, models, JSONField, \
    GA_GOALS_EA


class HitManager(models.Manager):
    def session_unification(self, hit, last_hit, expired, field_name):
        if (last_hit is None) or expired:
            return
        current_value = getattr(hit, field_name)
        if current_value != getattr(last_hit, field_name):
            previous_session_hits = self.filter(session_id=hit.session_id)
            for previous_hit in previous_session_hits:
                setattr(previous_hit, field_name, current_value)
                previous_hit.save()

    @transaction.atomic
    def create(self, hit_dict, trackable, userModel):
        hit = self.model()
        user = userModel.objects.user_auth(hit_dict, 'uid', trackable,
                                           self.model, 'cid')
        last_hit = trackable.get_last_hit(self.model)

        expired = hit.set_session_id(hit_dict, last_hit)
        hit.set_cid_user(trackable, user)
        self.session_unification(hit, last_hit, expired, 'user_id')
        hit.set_session_customs(hit_dict, last_hit, expired)
        hit.set_hit_customs(hit_dict)
        hit.set_session_attribution(hit_dict, last_hit, expired)
        self.session_unification(hit, last_hit, expired,
                                 'session_custom_dimensions')
        self.session_unification(hit, last_hit, expired,
                                 'session_custom_metrics')
        hit.set_event_attribution(hit_dict, trackable, user, expired, last_hit)
        hit.map_hit_dict(hit_dict)
        hit.set_other_variables(hit_dict)
        hit.save()

        trackable.update_last_hit(hit, self.model)
        return trackable, user, hit


class Hit(TimeStampedModel, Attributionable):
    other_keys = ['cid', 't', 'ec', 'ea', 'el', 'ev', 
                  'dt', 'dp', 'cn', 'ck', 'cs', 'cm']

    objects = HitManager()

    def set_session_id(self, hit_dict, last_hit):
        expired = last_hit.session_expired(hit_dict) \
            if last_hit is not None else True
        self.session_id = random_id() if expired \
            else last_hit.session_id
        return expired

    def session_expired(self, hit_dict):
        age = datetime.utcnow().replace(tzinfo=pytz.UTC) - self.created
        if age > timedelta(minutes=30):
            return True
        if 'cs' in hit_dict and 'cm' in hit_dict:
            return True
        return False

    def set_session_customs(self, hit_dict, last_hit, expired):
        metrics = get_variables(hit_dict, 'session', 'metric')
        dimensions = get_variables(hit_dict, 'session', 'dimension')
        if expired or last_hit is None:
            return metrics, dimensions
        old_metrics = last_hit.session_custom_metrics.copy()
        old_dimensions = last_hit.session_custom_dimensions.copy()
        old_metrics.update(metrics)
        old_dimensions.update(dimensions)
        self.session_custom_dimensions = old_dimensions
        self.session_custom_metrics = old_metrics

    def set_hit_customs(self, hit_dict):
        self.hit_custom_metrics = get_variables(hit_dict, 'hit', 'metric')
        self.hit_custom_dimensions = get_variables(hit_dict, 'hit', 'dimension')

    def set_session_attribution(self, hit_dict, last_hit, expired):
        if expired or last_hit is None:
            self.session_source = hit_dict.get('cs', 'unknown')
            self.session_medium = hit_dict.get('cm', 'unknown')
        else:
            self.session_source = last_hit.session_source
            self.session_medium = last_hit.session_medium
        self.campaign_name = hit_dict.get('cn', '')
        self.campaign_keyword = hit_dict.get('ck', '')

    def set_event_attribution(self, hit_dict, trackable, user, expired, 
                              last_hit):
        if (hit_dict.get('ea') in GA_GOALS_EA or '*' in GA_GOALS_EA) \
                and ((not expired and last_hit.lnd_attribution == {}) or expired):
            if user is not None:
                att_path = user.get_attribution_path(type(self), 'user_id')
            else:
                att_path = trackable.get_attribution_path(type(self), 'cid')
            self.lnd_attribution = trackable.lnd(att_path)
        elif (not expired) and last_hit.lnd_attribution != {}:
            self.lnd_attribution = last_hit.lnd_attribution

    def map_hit_dict(self, hit_dict):
        self.hit_type = hit_dict.get('t', 'unknown')
        self.event_category = hit_dict.get('ec', '')
        self.event_action = hit_dict.get('ea', '')
        self.event_label = hit_dict.get('el', '')
        self.event_value = hit_dict.get('ev')
        self.page_url = hit_dict.get('dp', '')
        self.page_name = hit_dict.get('dt', '')

    def set_other_variables(self, hit_dict):
        self.other_variables = {key: value for key, value in hit_dict.items()
                                if key not in self.other_keys}

    def set_cid_user(self, trackable, user):
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        self.cid = trackable.id
        self.cid_age = (now - trackable.created).days
        self.cid_meta = trackable.session_attribution
        if user is not None:
            self.user_id = user.id
            self.user_age = (now - user.created).days
            self.user_meta = {'first_session': user.session_attribution,
                              'lnd': user.lnd_attribution}
            user.update_known_cids(self)
            trackable.update_known_users(self)

    def update_info(self, info_dict):
        info = self.extra_info
        info.update(info_dict)
        self.extra_info = info
        self.save()

    cid = models.TextField(blank=True)
    user_id = models.TextField(blank=True)
    session_id = models.TextField()
    user_age = models.IntegerField(null=True)
    cid_age = models.IntegerField(null=True)
    user_meta = JSONField(default=dict)
    cid_meta = JSONField(default=dict) 

    hit_custom_metrics = JSONField(default=dict)
    hit_custom_dimensions = JSONField(default=dict)
    session_custom_metrics = JSONField(default=dict)
    session_custom_dimensions = JSONField(default=dict)

    session_source = models.TextField(default='unknown')
    session_medium = models.TextField(default='unknown')
    campaign_name = models.TextField(blank=True)
    campaign_keyword = models.TextField(blank=True)

    hit_type = models.TextField(default='unknown')
    page_url = models.TextField(blank=True)
    page_name = models.TextField(blank=True)

    event_category = models.TextField(blank=True)
    event_action = models.TextField(blank=True)
    event_label = models.TextField(blank=True)
    event_value = models.IntegerField(null=True)

    other_variables = JSONField(default=dict)
    extra_info = JSONField(default=dict)

    class Meta:
        abstract = True
        indexes = [
            models.Index(['event_action', '-created']),
            models.Index(['session_medium', '-created']),
            models.Index(['-created'])
        ]
