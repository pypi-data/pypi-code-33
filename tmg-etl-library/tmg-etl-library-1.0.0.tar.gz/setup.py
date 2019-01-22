from setuptools import setup, find_packages
import version

with open('requirements.txt') as f:
    required = f.read().splitlines()

# tests_require = [
#     required
# ]

packages = find_packages()

setup(
    name='tmg-etl-library',
    version=version.__version__,
    description='TMG Etl library',
    author='Data Platform team',
    packages=[package for package in packages if package != 'tests'],
    py_modules=['version'],
    # tests_require=tests_require,
    package_data={},
    install_requires=required
)
