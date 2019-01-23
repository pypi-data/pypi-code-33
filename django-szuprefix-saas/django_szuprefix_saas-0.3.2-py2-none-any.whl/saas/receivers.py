# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_szuprefix.auth.signals import to_get_user_profile
from . import models, serializers


@receiver(post_save, sender=models.Party)
def initDepartment(sender, **kwargs):
    party = kwargs['instance']
    if party.departments.count() == 0:
        party.departments.create(name=party.name)
    else:
        root = party.departments.get(parent__isnull=True)
        if root.name != party.name:
            root.name = party.name
            root.save()


@receiver(post_save, sender=models.Party)
def initWorker(sender, **kwargs):
    party = kwargs['instance']
    if party.workers.count() == 0:
        name = group_name = '%s管理员' % models.Party._meta.verbose_name
        worker = party.workers.create(name=name)
        worker.departments = party.departments.filter(parent__isnull=True)
        from django.contrib.auth.models import Group
        g = Group.objects.filter(name=group_name).first()
        if g:
            worker.user.groups.add(g)

@receiver(to_get_user_profile)
def get_worker_profile(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'as_saas_worker'):
        return serializers.CurrentWorkerSerializer(user.as_saas_worker, context=dict(request=kwargs['request']))
