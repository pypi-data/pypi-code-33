import pytz
import string
import random
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField


GA_VARIABLES = getattr(settings, "GA_CUSTOM_VARIABLES", None)


def get_variables(hit, variable_scope, variable_type):
    not_found = {'scope': None, 'type': None}
    return {key: value for key, value in hit.items()
            if GA_VARIABLES.get(key, not_found)['scope'] == variable_scope and
            GA_VARIABLES.get(key, not_found)['type'] == variable_type}


class User(TimeStampedModel):
    def update_custom_variables(self, hit):
        new_dimensions = get_variables(hit, 'user', 'dimension')
        new_metrics = get_variables(hit, 'user', 'metric')
        self.dimensions = self.dimensions.update(new_dimensions) \
            if self.dimensions is not None else new_dimensions
        self.metrics = self.metrics.update(new_metrics) \
            if self.metrics is not None else new_metrics
        self.save()
        return self

    def update_last_hit(self, hit):
        self.last_hit = hit
        self.save()
        return self

    cid = models.TextField(primary_key=True)
    user_id = models.TextField(blank=True)
    metrics = JSONField(null=True)
    dimensions = JSONField(null=True)
    last_hit = models.ForeignKey('Hit', null=True)


class HitManager(models.Manager):
    maped_keys = ['cid', 't', 'ec', 'ea', 'el', 'ev', 
                  'dt', 'dp', 'cn', 'ck', 'cs', 'cm']

    def random_id(self, size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def get_source_and_medium(self, hit, user):
        if user.last_hit is None:
            return hit.get('cs', None), hit.get('cm', None) 
        return hit.get('cs', user.last_hit.session_source), \
            hit.get('cm', user.last_hit.session_medium)

    def get_session_vars(self, hit, user, expired):
        metrics = get_variables(hit, 'session', 'metric')
        dimensions = get_variables(hit, 'session', 'dimension')
        if expired or user.last_hit is None:
            return metrics, dimensions
        old_metrics = user.last_hit.session_custom_metrics or {}
        old_dimensions = user.last_hit.session_custom_metrics or {}
        return old_metrics.update(metrics), old_dimensions.update(dimensions)

    def get_hit_and_user_vars(self, hit, user):
        metrics = get_variables(hit, 'hit', 'metric')
        dimensions = get_variables(hit, 'hit', 'dimension')
        return metrics.update(user.metrics or {}), \
            dimensions.update(user.dimensions or {})

    def other_variables(self, hit):
        return {key: value for key, value in hit.items()
                if key not in self.maped_keys}

    def create(self, hit, user):
        expired = user.last_hit.session_expired(hit) \
            if user.last_hit is not None else True
        session_metrics, session_dimensions = self.get_session_vars(hit,
                                                                    user,
                                                                    expired)
        metrics, dimensions = self.get_hit_and_user_vars(hit, user)
        source, medium = self.get_source_and_medium(hit, user)
        hit_model = Hit(
            cid=user,
            user_id=user.user_id,
            session_id=self.random_id() if expired
            else user.last_hit.session_id,
            session_custom_metrics=session_metrics,
            session_custom_dimensions=session_dimensions,
            custom_metrics=metrics,
            custom_dimensions=dimensions,
            session_source=source or 'unknown',
            session_medium=medium or 'unknown',
            hit_type=hit.get('t', 'unknown'),
            event_category=hit.get('ec', ''),
            event_action=hit.get('ea', ''),
            event_label=hit.get('el', ''),
            event_value=hit.get('ev'),
            campaign_name=hit.get('cn', ''),
            campaign_keyword=hit.get('ck', ''),
            page_url=hit.get('dp', ''),
            page_name=hit.get('dt', ''),
            other_variables=self.other_variables(hit)
        )
        hit_model.save()
        return hit_model


class Hit(TimeStampedModel):
    objects = HitManager()

    def session_expired(self, hit):
        age = datetime.utcnow().replace(tzinfo=pytz.UTC) - self.created
        if age > timedelta(minutes=30):
            return True
        if 'cs' in hit and 'cm' in hit:
            return True
        return False

    cid = models.ForeignKey('User')
    user_id = models.TextField(blank=True)
    session_id = models.TextField()
    custom_metrics = JSONField(null=True)
    custom_dimensions = JSONField(null=True)
    session_custom_metrics = JSONField(null=True)
    session_custom_dimensions = JSONField(null=True)
    session_source = models.TextField(default='unknown')
    session_medium = models.TextField(default='unkown')
    hit_type = models.TextField(default='unkown')
    event_category = models.TextField(blank=True)
    event_action = models.TextField(blank=True)
    event_label = models.TextField(blank=True)
    event_value = models.IntegerField(null=True)
    campaign_name = models.TextField(blank=True)
    campaign_keyword = models.TextField(blank=True)
    page_url = models.TextField(blank=True)
    page_name = models.TextField(blank=True)
    other_variables = JSONField(null=True)
