import setuptools
from sim_db import __version__

setuptools.setup(
        name='sim_db',
        version=__version__,
        scripts=['sim_db/sim_db', 'sim_db/sdb', 'sim_db/sim_db_cd.sh'],
        author='Hakon Austlid Tasken',
        author_email='hakon.tasken@gmail.com',
        description='A database for simulation parameters.',
        long_description=
        ('A command line tool and set of functions for '
         'conveniently running a large number of simulations with different '
         'parameter values, while keeping track of these all simulation '
         'parameters and results along with metadata in a database for you.'),
        url='http://sim-db.readthedocs.io',
        packages=setuptools.find_packages(),
        classifiers=[
                'Programming Language :: Python',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 3',
                'License :: OSI Approved :: MIT License',
        ],
        entry_points={
                'console_scripts': [
                        'sim_db = sim_db.__main__:sim_db',
                        'sdb = sim_db.__main__:sdb'
                ],
        },
        license='MIT License',
        include_package_data=True,
)
