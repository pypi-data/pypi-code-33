from .create_data import create_projectrole, create_projectpermission
from .create_data import create_user


def create_users_role():
    role_owner = create_projectrole(name='owner')
    perm_owner = create_projectpermission(name='owner')
    perm_owner.role.add(role_owner)

    role_manager = create_projectrole(name='manager')
    perm_manager = create_projectpermission(name='manager')
    perm_manager.role.add(role_owner)
    perm_manager.role.add(role_manager)

    role_member = create_projectrole(name='member')
    perm_member = create_projectpermission(name='member')
    perm_member.role.add(role_owner)
    perm_member.role.add(role_manager)
    perm_member.role.add(role_member)

    role_guess = create_projectrole(name='guess')
    perm_guess = create_projectpermission(name='private')
    perm_guess.role.add(role_owner)
    perm_guess.role.add(role_manager)
    perm_guess.role.add(role_member)
    perm_guess.role.add(role_guess)

    create_projectpermission(name='public')

    create_user(username='user1')
    create_user(username='user2')
    create_user(username='user3')
    create_user(username='user4')
    create_user(username='user5')
