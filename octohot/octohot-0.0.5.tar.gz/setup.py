from setuptools import setup

setup(
    name="octohot",
    version="0.0.5",
    description="A git command automation for multiple repositories",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Hotmart-Org/octohot",
    author="Jônatas Renan Camilo Alves",
    author_email="jonatas.alves@hotmart.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords='git automation github repositories',
    packages=['octohot'],
    install_requires=[
        'github3.py', 'click', 'pyyaml'
    ],
    include_package_data=True,
    package_data={
        'octohot': ['*.yml']
    },
    entry_points={'console_scripts': ['octohot = octohot.cli.cli:cli']}
)
