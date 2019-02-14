import logging
from rest_framework import authentication
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import Consumer
from .functions import extract_groups

from .settings import (KONG_CONSUMER_ID_HEADER,
                       KONG_ANONYMOUS_CONSUMER_ID,
                       KONG_ANONYMOUS_CONSUMER_HEADER,
                       KONG_CREATE_CONSUMER_GROUPS)


logger = logging.getLogger('django_rest_framework_kong_consumers.authentication')

def update_consumer_groups(user, groups):
    if KONG_CREATE_CONSUMER_GROUPS:
        for group in groups:
            if group != 'staff':
                g, _created = Group.objects.get_or_create(name=group)
                logger.info('Created group {}'.format(g))
                g.user_set.add(user)

def get_kong_user(request):

    is_anonymous = request.META.get(KONG_ANONYMOUS_CONSUMER_HEADER, None) is not None
    kong_consumer_id = request.META.get(KONG_CONSUMER_ID_HEADER, KONG_ANONYMOUS_CONSUMER_ID)
    groups = extract_groups(request.META.get('HTTP_X_CONSUMER_GROUPS', 'users'))
    is_staff = ('staff' in groups)

    logger.debug('Got kong_consumer_id: {}'.format(kong_consumer_id))

    # Consumer is anonymous
    if is_anonymous or kong_consumer_id == KONG_ANONYMOUS_CONSUMER_ID:
        logger.info('Kong says user is anonymous')
        return
      
    # Consumer is custom
    try:
        user = Consumer.objects.get(kong_consumer_id=kong_consumer_id)

    except Consumer.DoesNotExist:
        logger.info('kong_consumer_id: {} does not exists, creating with groups {}'.format(kong_consumer_id, groups))
        user = Consumer.objects.create_user(kong_consumer_id, is_staff=is_staff)
        update_consumer_groups(user, groups)
    else:
        _updated = False

        g1 = list(map(lambda x: x.name, user.groups.only('name')))
        g2 = list(filter(lambda x: x != 'staff', groups))
        if g1 != g2:
            logger.info('Groups updated from {} to {}'.format(g1, g2))
            user.groups.clear()
            update_consumer_groups(user, groups)
            _updated = True

        if is_staff and not user.is_staff:
            user.is_staff = True
            _updated = True

        if _updated:
            user.updated_at = timezone.now()
            user.save()

    return user


class KongConsumerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user = get_kong_user(request)
        logger.info('Athenticated as {}'.format(user))
        return (user, None)
