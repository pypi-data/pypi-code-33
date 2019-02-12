# 本文件定义了用于系统数据库的角色和选项
from Reger.options import SideBarOptions, SideBarOption
from Reger.models import get_session, Roles

mod_auth_opt = {
    'opt': [
        {
            'key': 'user_info',
            'title': '账户信息'
        },
        {
            'key': 'service_list',
            'title': '服务列表'
        },
        {
            'key': 'module_reg',
            'title': '注册服务'
        },
        {
            'key': 'mod_manage',
            'title': '服务管理',
        }
    ],
}
mod_auth = SideBarOptions('mod_auth', 0b0010, mod_auth_opt['opt'])


super_admin_opt = {
    'opt': [
        {
            'key': 'user_manage',
            'title': '用户管理',
        },
    ]
}
super_admin = SideBarOptions('super_admin', 0b0001, super_admin_opt['opt'])

def store(role: SideBarOptions):
    session = get_session()
    r = Roles()
    r.name = role.name
    r.info = role.to_json()
    r.code = role.code
    session.add(r)
    session.commit()

if __name__ == '__main__':
    # print(super_admin.to_json(indent=4))
    store(mod_auth)
    store(super_admin)