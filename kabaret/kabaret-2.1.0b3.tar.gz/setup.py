import os
import sys
from setuptools import setup, find_packages


# (
#    (Major, Minor, [Micros]),
#    [(releaselevel, serial)],
# )
#__version_info__ = ((1, 0, 0),)
#__version_info__ = ((1, 0, 0),(rc,))
#__version_info__ = ((1, 0, 0),(rc,1))
__version_info__ = ((2, 1, 0), ('b', 3))


if 0:
    long_description = (
        'VFX/Animation Studio Framework '
        'tailored for TDs/Scripters '
        'managing pipelines and workflows '
        'used by Production Managers and CGI Artists.\n\n'
        'Read the doc here: http://kabaret.readthedocs.io'
    )
else:
    readme = os.path.normpath(os.path.join(__file__, '..', 'README.rst'))
    with open(readme, 'r') as fh:
        long_description = fh.read()

    long_description += '\n\n'
    changelog = os.path.normpath(os.path.join(__file__, '..', 'CHANGELOG.md'))
    with open(changelog, 'r') as fh:
        long_description += fh.read()


def get_version():
    global __version_info__
    return (
        '.'.join(str(x) for x in __version_info__[0])
        + ''.join(str(x) for x in __version_info__[1])
    )


setup(
    name='kabaret',
    version=get_version(),
    description='VFX/Animation Studio Framework',
    long_description=long_description,
    url='http://www.kabaretstudio.com',
    author='Damien dee Coureau',
    author_email='kabaret-dev@googlegroups.com',
    license='LGPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',

        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Office/Business :: Scheduling',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',

        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    ],
    keywords='vfx animation framewok dataflow workflow asset manager production tracker',
    install_requires=[
        'redis<3.0.0',
        'six',
        'qtpy',
    ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',
    packages=find_packages('python'),
    package_dir={'': 'python'},
    package_data={
        '': ['*.css', '*.png', '*.svg', '*.gif'],
    },
)
