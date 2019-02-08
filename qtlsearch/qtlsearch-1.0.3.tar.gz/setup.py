'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch.

    QTLSearch is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    QTLSearch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with QTLSearch.  If not, see <http://www.gnu.org/licenses/>.
'''
from setuptools import setup, find_packages

name = 'qtlsearch'
__version__ = None
with open('{:s}/__init__.py'.format(name), 'rt') as fp:
    for line in fp:
        if line.startswith('__version__'):
            exec(line.rstrip())

requirements = ['appdirs', 'biopython', 'dendropy', 'lxml', 'numpy', 
                'pandas', 'property_manager', 'requests', 'requests_cache',
                'scipy', 'tables', 'tqdm', 'wget']

desc='Uses OMA\'s HOGs to predict genes related to QTL.'

setup(
    name=name,
    version=__version__,
    author='Alex Warwick Vesztrocy',
    author_email='alex@warwickvesztrocy.co.uk',
    url='https://bitbucket.org/alex-warwickvesztrocy/qtlsearch',
    description=desc,
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.6",
    license='LGPLv3',
    scripts=['bin/qtlsearch-init', 'bin/qtlsearch-run'])
