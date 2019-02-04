from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="awssearch",
    version="0.0.4",
    description="A AWS Search tool",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Hotmart-Org/awssearch",
    author="Jonatas Renan Camilo Alves",
    author_email="jonatas.alves@hotmart.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords='aws search tool',
    packages=['awssearch'],
    install_requires=requirements,
    include_package_data=True,
    entry_points={'console_scripts': ['awssearch = awssearch.cli.cli:cli']}
)
