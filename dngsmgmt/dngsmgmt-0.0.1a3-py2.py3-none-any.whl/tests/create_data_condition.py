from django.contrib.auth.models import User

from ..models import ProjectPermission, Experiment, Sample
from .create_data import create_condition, create_conditionmetadata
from .create_data_sample import create_samples


def create_conditions():
    create_samples()
    user2 = User.objects.get(username='user2')
    user4 = User.objects.get(username='user4')

    perm_owner = ProjectPermission.objects.get(name='owner')
    perm_manager = ProjectPermission.objects.get(name='manager')
    perm_public = ProjectPermission.objects.get(name='public')

    experiment = Experiment.objects.get(pk=1)
    condition = create_condition(name='Condition1',
                                 permission=perm_public,
                                 created_by=user2,
                                 updated_by=user2,
                                 experiment=experiment)

    create_conditionmetadata(key='tissue', value='Lung cancer',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    create_conditionmetadata(key='cell', value='H69AR',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    sample = Sample.objects.get(pk=1)
    condition.samples.add(sample)

    condition = create_condition(name='Condition2',
                                 permission=perm_public,
                                 created_by=user2,
                                 updated_by=user2,
                                 experiment=experiment)

    create_conditionmetadata(key='tissue', value='Lung',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    create_conditionmetadata(key='cell', value='H69AR',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    sample = Sample.objects.get(pk=2)
    condition.samples.add(sample)
    sample = Sample.objects.get(pk=3)
    condition.samples.add(sample)

    condition = create_condition(name='Condition3',
                                 permission=perm_manager,
                                 created_by=user2,
                                 updated_by=user2,
                                 experiment=experiment)

    create_conditionmetadata(key='tissue', value='Lung cancer',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    create_conditionmetadata(key='cell', value='H69AR',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    sample = Sample.objects.get(pk=1)
    condition.samples.add(sample)
    sample = Sample.objects.get(pk=2)
    condition.samples.add(sample)

    condition = create_condition(name='Condition4',
                                 permission=perm_manager,
                                 created_by=user2,
                                 updated_by=user2,
                                 experiment=experiment)

    create_conditionmetadata(key='tissue', value='Lung',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)
    create_conditionmetadata(key='cell', value='H69AR',
                             condition=condition,
                             created_by=user2,
                             updated_by=user2)

    sample = Sample.objects.get(pk=3)
    condition.samples.add(sample)

    experiment = Experiment.objects.get(pk=3)
    condition = create_condition(name='Condition5',
                                 permission=perm_owner,
                                 created_by=user4,
                                 updated_by=user4,
                                 experiment=experiment)

    create_conditionmetadata(key='tissue', value='Lung cancer',
                             condition=condition,
                             created_by=user4,
                             updated_by=user4)
    create_conditionmetadata(key='cell', value='H69AR',
                             condition=condition,
                             created_by=user4,
                             updated_by=user4)
    sample = Sample.objects.get(pk=4)
    condition.samples.add(sample)
