from distutils.core import setup

requires = []
try:
    import mercurial
    mercurial.__all__
except ImportError:
    requires.append('mercurial')

setup(
    name='hgenvconfig',
    version='0.1.2',
    author='Sean Farley',
    author_email='sean@farley.io',
    maintainer='Sean Farley',
    maintainer_email='sean@farley.io',
    url='http://bitbucket.org/seanfarley/hgenvconfig/',
    description=('A Mercurial enxtension to pass config options '
                 'via an environment variable.'),
    long_description=open('README').read(),
    keywords='hg mercurial',
    license='GPLv2+',
    packages=['hgext'],
    install_requires=requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public '
        'License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
