from distutils.core import setup   #从发布工具导入setup函数

setup(
    name = 'wvely',
    version = '1.0.1',
    py_modules = ['wvely'], #将模块的元数据与setup函数的参数关联
    author = 'wangvely',
    author_email = '781224336@qq.com',
    url = 'http://www.headfirstlabs.com',
    description = 'A simple printer of lists'
)