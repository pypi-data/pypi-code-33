from setuptools import find_packages, setup

setup(
    name='trex_stl_lib',
    version='0.1',
    description='Trex Stateless library',

    url='https://github.com/dedie/trex_stl_lib',
    author='Daron Edie',
    author_email='darby69@gmail.com',
    license='Apache',
    zip_safe=False,

    packages=find_packages('src', exclude=['test']),
    package_dir={'': 'src'},

    install_requires=[
        'scapy',
        'simpy',
        'pyzmq',
        'texttable',
        'pyyaml',
        'jsonrpclib-pelix',
    ],
)
