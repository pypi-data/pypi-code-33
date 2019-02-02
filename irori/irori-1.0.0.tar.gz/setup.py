from setuptools import setup, find_packages
from os import path


root_dir = path.abspath(path.dirname(__file__))
package_name = 'irori'


def _requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements.txt')).readlines()]


setup(
    name='irori',
    version='1.0.0',
    license='GPLv3.0',
    packages=find_packages(),

    install_requires=_requirements(),

    author='SiLeader',
    url='https://github.com/SiLeader/irori',

    description='general purpose built tool',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Japanese',
        'Natural Language :: English',

        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: POSIX',

        'Topic :: Software Development :: Build Tools'
    ]
)
