from setuptools import setup, find_packages
import vac_exporter

setup(
    name='vac_exporter',
    version=vac_exporter.__version__,
    author=vac_exporter.__author__,
    description='Veeam VAC Exporter for Prometheus',
    long_description=open('README.md').read(),
    url='https://gitlab.com/frenchtoasters/vac_exporter',
    keywords=['Veeam', 'VAC', 'Prometheus'],
    license=vac_exporter.__license__,
    packages=find_packages(exclude=['*.test', '*.test.*']),
    include_package_data=True,
    install_requires=open('requirements.txt').readlines(),
    entry_points={
        'console_scripts': [
            'vac_exporter=vac_exporter.vac_cli:main'
        ]
    }
)
