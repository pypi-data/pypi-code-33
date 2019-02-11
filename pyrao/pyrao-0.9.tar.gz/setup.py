"""Setup.py module."""


"""ПОПРОБОВАТЬ ЗАЛИТЬ НА pip SOURCES И УСТАНОВИТЬ С ОПЦИОНАЛЬНЫМ АРГУМЕНТОМ"""
import sys
from setuptools import setup, find_packages, Extension, command
from setuptools.command.build_py import build_py as build_py_orig
from fnmatch import fnmatchcase

try:
    import numpy as np
except ImportError:
    import pip
    if hasattr(pip, 'main'):
        pip.main(['install', 'numpy'])
    else:
        import pip._internal as internal
        internal.main(['install', 'numpy'])
        import numpy as np

exclude = []

class build_py(build_py_orig):

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [(pkg, mod, file, ) for (pkg, mod, file, ) in modules
                if not any(fnmatchcase(f'{pkg}.{mod}', pat=pattern)
                for pattern in exclude)]

configuration = dict(
    name='pyrao',
    version='0.9',
    description='Toolkit designed to integrate BSA structures \
                 with the most recent world astronomic practices.',
    license="GNUv3",
    author='Alexander S.',
    # author_email='',
    url='https://github.com/AlexanderBBI144/PyRAO/',
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'matplotlib', 'angles', 'astropy',
                      'scipy'],
    zip_safe=False,
    cmdclass={'build_py': build_py},
)

platform_name = ''
if '-p' in sys.argv:
    platform_name = sys.argv[sys.argv.index('-p') + 1]
elif '--plat-name' in sys.argv:
    platform_name = sys.argv[sys.argv.index('-p') + 1]

if 'win' in platform_name:
    configuration['include_package_data'] = True
else:
    exclude = ['*cinterp1d']
    configuration['ext_modules'] = [Extension("pyrao.integration.cinterp1d",
                                              ["pyrao/integration/cinterp1d.c"],
                                              include_dirs=[np.get_include()],
                                              build_dir="pyrao/integration")]

setup(**configuration)
