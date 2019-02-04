import os
import sys
from setuptools import setup, find_packages


# (
#    (Major, Minor, [Micros]),
#    [(releaselevel, serial)],
# )
#__version_info__ = ((1, 0, 0),())
#__version_info__ = ((1, 0, 0),(rc,))
#__version_info__ = ((1, 0, 0),(rc,1))
__version_info__ = ((0, 0, 0), ('a', 2))


readme = os.path.normpath(os.path.join(__file__, '..', 'README.md'))
with open(readme, 'r') as fh:
    long_description = fh.read()

# long_description += '\n\n'
# changelog = os.path.normpath(os.path.join(__file__, '..', 'CHANGELOG.md'))
# with open(changelog, 'r') as fh:
#     long_description += fh.read()


def get_version():
    global __version_info__
    return (
        '.'.join(str(x) for x in __version_info__[0])
        + ''.join(str(x) for x in __version_info__[1])
    )


setup(
    name='kabaret.ingrid',
    version=get_version(),
    description='A Grid/Table view for the Kabaret framework flow objects',
    long_description=long_description,
    url='https://gitlab.com/kabaretstudio/kabaret.ingrid',
    author='Damien "dee" Coureau',
    author_email='kabaret-dev@googlegroups.com',
    license='LGPLv3+',
    classifiers=[
        #'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial :: Spreadsheet',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',

        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    ],
    keywords='kabaret vfx animation spreadsheet pipeline dataflow workflow asset manager',
    install_requires=[
        'kabaret>=2.1.0b1',
    ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',
    packages=find_packages('python'),
    package_dir={'': 'python'},
    package_data={
        '': ['*.css', '*.png', '*.svg', '*.gif'],
    },
)
