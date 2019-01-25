from django.contrib.auth.models import User

from ..models import ProjectPermission, Project
from .create_data import create_experimenttype, create_experiment
from .create_data import create_experimentmetadata
from .create_data_project import create_projects


def create_experiments():
    create_projects()
    user2 = User.objects.get(username='user2')
    user3 = User.objects.get(username='user3')
    user4 = User.objects.get(username='user4')

    perm_owner = ProjectPermission.objects.get(name='owner')
    perm_manager = ProjectPermission.objects.get(name='manager')
    perm_public = ProjectPermission.objects.get(name='public')

    exp_type = create_experimenttype(name='RNA-Seq')

    project = Project.objects.get(pk=1)
    experiment = create_experiment(name='Experiment1',
                                   description='My experiment number 1',
                                   project=project,
                                   permission=perm_owner,
                                   type=exp_type,
                                   created_by=user2,
                                   updated_by=user2)

    create_experimentmetadata(key='tissue', value='Lung cancer',
                              experiment=experiment,
                              created_by=user2,
                              updated_by=user2)
    create_experimentmetadata(key='cell', value='H69AR',
                              experiment=experiment,
                              created_by=user2,
                              updated_by=user2)

    project = Project.objects.get(pk=2)
    experiment = create_experiment(name='Experiment2',
                                   description='My experiment number 2',
                                   project=project,
                                   permission=perm_manager,
                                   type=exp_type,
                                   created_by=user2,
                                   updated_by=user2)
    create_experimentmetadata(key='tissue', value='Lung cancer',
                              experiment=experiment,
                              created_by=user2,
                              updated_by=user2)
    create_experimentmetadata(key='cell', value='H69AR',
                              experiment=experiment,
                              created_by=user2,
                              updated_by=user2)

    project = Project.objects.get(pk=3)
    experiment = create_experiment(name='Experiment3',
                                   description='My experiment number 3',
                                   project=project,
                                   permission=perm_manager,
                                   type=exp_type,
                                   created_by=user3,
                                   updated_by=user3)
    create_experimentmetadata(key='tissue', value='Lung cancer',
                              experiment=experiment,
                              created_by=user3,
                              updated_by=user3)
    create_experimentmetadata(key='cell', value='H69AR',
                              experiment=experiment,
                              created_by=user3,
                              updated_by=user3)

    project = Project.objects.get(pk=4)
    experiment = create_experiment(name='Experiment4',
                                   description='My experiment number 4',
                                   project=project,
                                   permission=perm_public,
                                   type=exp_type,
                                   created_by=user4,
                                   updated_by=user4)
    create_experimentmetadata(key='tissue', value='Lung cancer',
                              experiment=experiment,
                              created_by=user4,
                              updated_by=user4)
    create_experimentmetadata(key='cell', value='H69AR',
                              experiment=experiment,
                              created_by=user4,
                              updated_by=user4)
