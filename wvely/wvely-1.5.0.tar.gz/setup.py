from distutils.core import setup

#提供模块的元数据  用来构建，安装和上传打包的发布
setup(
    name = 'wvely',
    version = '1.5.0',
    py_modules = ['wvely'],  #将模块的元数据与setup函数的参数关联
    author = 'wvely',
    author_email= '781224336@qq.com',
    url = 'http://www.headfirstlabs.com',
    description= 'A simple printer of lists'
)