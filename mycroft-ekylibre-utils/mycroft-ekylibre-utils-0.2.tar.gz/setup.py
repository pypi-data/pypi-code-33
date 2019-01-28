from setuptools import setup, find_packages

setup(
    name='mycroft-ekylibre-utils',
    version='0.2',
    packages=find_packages(),
    url='http://github.com/ekylibre',
    license='Apache License 2.0',
    author='Ekylibre',
    author_email='rdechazelles@ekylibre.com',
    description='Ekylibre set of tools for MycroftAI skills',
    long_description=open('README.rst').read(),
    install_requires=["requests"],
    include_package_data=True,
)
