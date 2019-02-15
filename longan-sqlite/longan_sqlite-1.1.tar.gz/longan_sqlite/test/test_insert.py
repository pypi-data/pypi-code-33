from longan_sqlite import *

Longan.init('test.db', debug=True)
longan = Longan('company')


def bundle():
    # 批量插入或修改
    flesh_list = [
        Flesh(name='jobs', age=50, address='America', salary=90),
        Flesh(name='杰克马', age=45, address='china', salary=70),
        Flesh(name='黄鹤', age=32, address='china', salary=2),
        Flesh(name='baby', age=4, address='china', salary=-5),
        Flesh(name='金三瘦', age=35, address='朝鲜', salary=900)
    ]
    longan.insert_or_update(*flesh_list)


def single():
    # 单独插入
    flesh = Flesh(name='emperor', age=23, address='北京', salary=10)
    longan.insert_or_update(flesh)
