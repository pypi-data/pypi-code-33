# coding=utf-8
from setuptools import setup
import nf.__version__ as version
import distutils.util

try:
    from wheel.bdist_wheel import bdist_wheel

    class _bdist_wheel(bdist_wheel):
        def get_tag(self):
            tag = bdist_wheel.get_tag(self)
            platform_tag = {
                'win32': 'win32',
                'win-amd64': 'win_amd64',
                'linux-x86_64': 'manylinux1_x86_64'
            }
            python_ver = tag[0]
            if python_ver == 'py27':
                python_ver = 'py2'
            if python_ver == 'py34':
                python_ver = 'py3'
            tag = (python_ver, tag[1], platform_tag[distutils.util.get_platform()])
            return tag

    cmdclass = {'bdist_wheel': _bdist_wheel}
except ImportError:
    cmdclass = {}


install_requires = [
    'typing',
    'arrow',
    'grpcio',
    'Cython',
    'protobuf',
]

# dependency_links = [
#     'https://download.lfd.uci.edu/pythonlibs/j1ulh5xc/TA_Lib-0.4.17-cp37-cp37m-win_amd64.whl',
# ]


setup(
    name=version.__title__,
    version=version.__version__,
    description=version.__description__,
    url=version.__url__,
    author=version.__author__,
    author_email=version.__author_email__,
    license=version.__license__,
    include_package_data=True,

    # 要打的包的所有文件夹
    packages=['nf', 'nf.model', 'nf.api', 'nf.pb', 'nf.csdk', 'nf.csdk.lib',
              'github.com', 'github.com.gogo', 'github.com.gogo.protobuf',
              'github.com.gogo.protobuf.gogoproto', 'google.api',
              'nf.pb.auth', 'nf.pb.core', 'nf.pb.data', 'nf.pb.strategy',
              'nf.pb.trade', 'nf.pb.tradegw',

              'nf.pb.auth.api', 'nf.pb.auth.api.auth',
              'nf.pb.core.api', 'nf.pb.core.api.report',
              'nf.pb.data.api',
              'nf.pb.strategy.api', 'nf.pb.strategy.api.strategy',
              'nf.pb.strategy.strategy_params.strategy',
              'nf.pb.trade.api', 'nf.pb.trade.api.trade',
              'nf.pb.tradegw.api', 'nf.pb.tradegw.api.tradegw',
              'nf.pb.gogoproto',
              'third_lib'
              ],
    zip_safe=False,
    # 依赖库
    install_requires=install_requires,
    # dependency_links=dependency_links,
    extras_require={
        'pandas': ['pandas'],
    },
    # 包对应文件
    package_dir={
        'nf': './nf',
        'nf.api': './nf/api',
        'github': './github',
        'google': './google',
        'nf.csdk:': './nf/csdk',
        'nf.csdk.lib:': './nf/csdk',
        'nf.model:': './nf/model',
        'nf.pb': './nf/pb',
        'nf.pb.auth': './nf/pb/auth',
        'nf.pb.core': './nf/pb/core',
        'nf.pb.data': './nf/pb/data',
        'nf.pb.strategy': './nf/pb/strategy',
        'nf.pb.trade': './nf/pb/trade',
        'nf.pb.tradegw': './nf/pb/tradegw',

        'nf.pb.auth.api': './nf/pb/auth/api',
        'nf.pb.auth.api.auth': './nf/pb/auth/api/auth',

        'nf.pb.gogoproto': './nf/pb/gogoproto',

        'nf.pb.core.api': './nf/pb/core/api',
        'nf.pb.core.api.report': './nf/pb/core/api/report',

        'nf.pb.data.api': './nf/pb/data/api',
        'nf.pb.strategy.api': './nf/pb/strategy/api',
        'nf.pb.strategy.api.strategy': './nf/pb/strategy/api/strategy',
        'nf.pb.strategy.strategy_params.strategy': './nf/pb/strategy/strategy_params/strategy',

        'nf.pb.trade.api': './nf/pb/trade/api',
        'nf.pb.trade.api.trade': './nf/pb/trade/api/trade',

        'nf.pb.tradegw.api': './nf/pb/tradegw/api',
        'nf.pb.tradegw.api.tradegw': './nf/pb/tradegw/api/tradegw',

        'github.com': './github/com',
        'github.com.gogo': './github/com/gogo',
        'github.com.gogo/protobuf': './github/com/gogo/protobuf',
        'github.com.gogo/protobuf/gogoproto': './github/com/gogo/protobuf/gogoproto',
        'third_lib': './third_lib'
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    # 命名空间， 要么有 __init__.py  要么就要一个写一遍
    namespace_packages=[
        'nf',
        'google',
        'github',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4',
    cmdclass=cmdclass,
    package_data={
        'nf.csdk': ['*.so'],
        'third_lib': ['third_lib/TA_Lib-0.4.17-cp37-cp37m-win_amd64.whl'],
    },
)
