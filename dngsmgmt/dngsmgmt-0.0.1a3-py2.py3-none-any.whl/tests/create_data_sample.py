from django.contrib.auth.models import User

from ..models import ProjectPermission, Experiment
from .create_data import create_sample, create_samplemetadata
from .create_data_experiment import create_experiments


def create_samples():
    create_experiments()
    user2 = User.objects.get(username='user2')
    user4 = User.objects.get(username='user4')

    perm_owner = ProjectPermission.objects.get(name='owner')
    perm_manager = ProjectPermission.objects.get(name='manager')
    perm_public = ProjectPermission.objects.get(name='public')

    experiment = Experiment.objects.get(pk=1)
    sample = create_sample(name='Sample1',
                           permission=perm_public,
                           created_by=user2,
                           updated_by=user2,
                           experiment=experiment)

    create_samplemetadata(key='tissue', value='Lung cancer',
                          sample=sample,
                          created_by=user2,
                          updated_by=user2)
    create_samplemetadata(key='cell', value='H69AR',
                          sample=sample,
                          created_by=user2,
                          updated_by=user2)

    sample = create_sample(name='Sample2',
                           permission=perm_manager,
                           created_by=user2,
                           updated_by=user2,
                           experiment=experiment)

    create_samplemetadata(key='tissue', value='Lung cancer',
                          sample=sample,
                          created_by=user2,
                          updated_by=user2)
    create_samplemetadata(key='cell', value='H69AR',
                          sample=sample,
                          created_by=user2,
                          updated_by=user2)

    experiment = Experiment.objects.get(pk=1)
    sample = create_sample(name='Sample3',
                           experiment=experiment,
                           permission=perm_manager,
                           created_by=user2,
                           updated_by=user2)
    create_samplemetadata(key='tissue', value='Lung cancer',
                          sample=sample,
                          created_by=user2,
                          updated_by=user2)
    create_samplemetadata(key='cell', value='H69AR',
                          sample=sample,
                          created_by=user2,
                          updated_by=user2)

    experiment = Experiment.objects.get(pk=3)
    sample = create_sample(name='Sample4',
                           experiment=experiment,
                           permission=perm_owner,
                           created_by=user4,
                           updated_by=user4)
    create_samplemetadata(key='tissue', value='Lung cancer',
                          sample=sample,
                          created_by=user4,
                          updated_by=user4)
    create_samplemetadata(key='cell', value='H69AR',
                          sample=sample,
                          created_by=user4,
                          updated_by=user4)
