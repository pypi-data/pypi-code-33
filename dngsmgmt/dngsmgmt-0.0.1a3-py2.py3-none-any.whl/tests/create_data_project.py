from django.contrib.auth.models import User

from ..models import ProjectRole, ProjectPermission

from .create_data import create_project, create_projectmetadata
from .create_data import create_projectuserrole
from .create_data_users import create_users_role


def create_projects():
    create_users_role()
    user1 = User.objects.get(username='user1')
    user2 = User.objects.get(username='user2')
    user3 = User.objects.get(username='user3')
    user4 = User.objects.get(username='user4')

    role_owner = ProjectRole.objects.get(name='owner')
    role_manager = ProjectRole.objects.get(name='manager')
    role_member = ProjectRole.objects.get(name='member')
    role_guess = ProjectRole.objects.get(name='guess')

    perm_owner = ProjectPermission.objects.get(name='owner')
    perm_manager = ProjectPermission.objects.get(name='manager')
    perm_guess = ProjectPermission.objects.get(name='private')
    perm_public = ProjectPermission.objects.get(name='public')

    project = create_project(name='User1 owner project',
                             permission=perm_owner,
                             created_by=user1,
                             updated_by=user1)
    create_projectmetadata(key='institution', value='NCBI',
                           project=project,
                           created_by=user1,
                           updated_by=user1)
    create_projectmetadata(key='source', value='human',
                           project=project,
                           created_by=user1,
                           updated_by=user1)

    create_projectuserrole(project=project, user=user1, role=role_owner)
    create_projectuserrole(project=project, user=user2, role=role_manager)
    create_projectuserrole(project=project, user=user3, role=role_member)
    create_projectuserrole(project=project, user=user4, role=role_guess)

    project = create_project(name='User2 owner project',
                             permission=perm_manager,
                             created_by=user2,
                             updated_by=user2)
    create_projectmetadata(key='institution', value='UCSC',
                           project=project,
                           created_by=user2,
                           updated_by=user2)
    create_projectmetadata(key='source', value='fly',
                           project=project,
                           created_by=user2,
                           updated_by=user2)

    create_projectuserrole(project=project, user=user1, role=role_owner)
    create_projectuserrole(project=project, user=user2, role=role_manager)
    create_projectuserrole(project=project, user=user3, role=role_member)
    create_projectuserrole(project=project, user=user4, role=role_guess)

    project = create_project(name='User3 owner project',
                             permission=perm_manager,
                             created_by=user3,
                             updated_by=user3)
    create_projectmetadata(key='institution', value='UM',
                           project=project,
                           created_by=user3,
                           updated_by=user3)
    create_projectmetadata(key='source', value='physalis',
                           project=project,
                           created_by=user3,
                           updated_by=user3)

    create_projectuserrole(project=project, user=user3, role=role_owner)
    create_projectuserrole(project=project, user=user4, role=role_manager)
    create_projectuserrole(project=project, user=user2, role=role_member)
    create_projectuserrole(project=project, user=user1, role=role_guess)

    project = create_project(name='User4 owner project',
                             permission=perm_guess,
                             created_by=user4,
                             updated_by=user4)
    create_projectmetadata(key='institution', value='NCI',
                           project=project,
                           created_by=user4,
                           updated_by=user4)
    create_projectmetadata(key='source', value='banana',
                           project=project,
                           created_by=user4,
                           updated_by=user4)

    create_projectuserrole(project=project, user=user3, role=role_owner)
    create_projectuserrole(project=project, user=user4, role=role_manager)
    create_projectuserrole(project=project, user=user2, role=role_member)
    create_projectuserrole(project=project, user=user1, role=role_guess)

    project = create_project(name='Public project',
                             permission=perm_public,
                             created_by=user4,
                             updated_by=user4)
    create_projectmetadata(key='institution', value='NIH',
                           project=project,
                           created_by=user4,
                           updated_by=user4)
    create_projectmetadata(key='source', value='mouse',
                           project=project,
                           created_by=user4,
                           updated_by=user4)

    create_projectuserrole(project=project, user=user3, role=role_owner)
    create_projectuserrole(project=project, user=user4, role=role_manager)
    create_projectuserrole(project=project, user=user2, role=role_member)
    create_projectuserrole(project=project, user=user1, role=role_guess)
