from setuptools import setup

setup(
    name='flatast',
    version='0.0.10',
    license='Apache 2.0',
    author='Yijun Yu',
    author_email='y.yu@open.ac.uk',
    url='https://bitbucket.org/yijunyu/fast',
    long_description=('Python runtime library for flat AST'
                      'serialization format.'),
    packages=['fast_', 'fast_.Data_', 'fast_.Graph_', 'fast_.Data_', 'flatast'],
    include_package_data=True,
    entry_points={'console_scripts': [
        'jira_crawler=flatast.jira_crawler:main', 
        'ggnn=flatast.flatast2ggnn:main' 
        ]},
    install_requires=['flatbuffers', 'protobuf', 'urllib3', 'bs4', 'lxml'],
    requires=['flatbuffers', 'protobuf', 'urllib3', 'bs4', 'lxml'],
    description='The FlatAST serialization format for Python',
)
