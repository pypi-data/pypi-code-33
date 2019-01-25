from .models import ProjectUserRole


def is_object_excluded(user, project, object):
    try:
        user_role = ProjectUserRole.objects.get(user=user,
                                                project=project)
        if object.permission.name == 'owner' and user_role.role.name != 'owner':
            return True
        elif object.permission.name == 'manager' and \
                user_role.role.name != 'owner' and \
                user_role.role.name != 'manager':
            return True
        elif object.permission.name == 'member' and \
                user_role.role.name != 'owner' and \
                user_role.role.name != 'manager' and \
                user_role.role.name != 'member':
            return True
        elif object.permission.name == 'guest' and \
                user_role.role.name != 'owner' and \
                user_role.role.name != 'manager' and \
                user_role.role.name != 'member' and \
                user_role.role.name != 'guest':
            return True
    except ProjectUserRole.DoesNotExist:
        return True
    return False
