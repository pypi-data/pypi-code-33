from distutils.core import setup
setup(
    name='ovl',
    packages=['ovl'],
    version='0.2.3',
    license='apache-2.0',
    author='Ori Ben-Moshe',
    author_email='ovl.contact.help@gmail.com',
    description='A python Module for Object tracking vision for Robots',
    url='https://github.com/1937Elysium/Ovl-Python',
    install_requires=['numpy', 'sklearn', 'pynetworktables', 'scipy'],
    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 ]
     )