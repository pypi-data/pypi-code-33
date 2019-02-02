from homevee.Helper.helper_functions import has_permission

def get_permissions(username, db):
    cur = db.cursor()
    cur.execute("SELECT * FROM 'userdata' WHERE USERNAME == :username",
                {'username': username})

    data = cur.fetchone()

    return data

def contains_permission(permissions, permission):
    return ('admin' in permissions or permission in permissions)

def set_permissions(username, permission_user, permissions, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    cur = db.cursor()
    cur.execute("UPDATE 'userdata' SET PERMISSIONS = :permissions WHERE USERNAME == :username",
                {'username':permission_user, 'permissions':permissions})

    return {'status': 'ok'}