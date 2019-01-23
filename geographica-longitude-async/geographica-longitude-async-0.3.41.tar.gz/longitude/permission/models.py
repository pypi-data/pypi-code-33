from longitude.models.sql import SQLCRUDModel


class RoleModel(SQLCRUDModel):

    table_name = 'longitude_permission_role'

    filters = {
        'is_admin': '_t.is_admin=%',
        'name': '_t.name=%'
    }
