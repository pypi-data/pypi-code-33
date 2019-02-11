from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mycroft-ekylibre-utils',
    version='0.7',
    packages=find_packages(),
    url='http://github.com/ekylibre',
    author='Ekylibre',
    author_email='rdechazelles@ekylibre.com',
    description='Ekylibre set of tools for MycroftAI skills',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    install_requires=["requests", 'urllib3'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
