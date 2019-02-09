from distutils.core import setup        #从python发布工具导入setup函数

setup(
    name         = 'printlist190209',                    # 包名
    version      = '3.3.0',                              # 版本号
    py_modules   = ['printlist'],
    author       = 'sonia',
    author_email = 'sonia_du@163.com',
    url          = 'http://www.devlve.top',
    description  = "printlist190209模块，提供了一个名为printlist()的函数,这个函数的作用是显示列表，其中有可能包含（也可能不包含）嵌套列表。",
    )
    
