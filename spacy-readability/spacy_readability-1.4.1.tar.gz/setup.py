# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['spacy_readability']

package_data = \
{'': ['*']}

install_requires = \
['spacy>=2.0,<3.0', 'syllapy>=0,<1']

setup_kwargs = {
    'name': 'spacy-readability',
    'version': '1.4.1',
    'description': 'spaCy pipeline component for adding text readability meta data to Doc objects.',
    'long_description': 'spacy_readability\n ==================\n \n  spaCy v2.0 pipeline component for calculating readability scores of of\n text. Provides scores for Flesh-Kincaid grade level, Flesh-Kincaid\n reading ease, Dale-Chall, and SMOG.\n \n  Installation\n ------------\n \n  ``` {.sourceCode .python}\n pip install spacy-readability\n ```\n \n  Usage\n -----\n \n  ``` {.sourceCode .python}\n import spacy\n from spacy_readability import Readability\n \n nlp = spacy.load(\'en\')\n read = Readability(nlp)\n nlp.add_pipe(read, last=True)\n \n doc = nlp("I am some really difficult text to read because I use obnoxiously large words.")\n \n print(doc._.flesch_kincaid_grade_level)\n print(doc._.flesch_kincaid_reading_ease)\n print(doc._.dale_chall)\n print(doc._.smog)\n print(doc._.coleman_liau_index)\n print(doc._.automated_readability_index)\n print(doc._.forcast)\n ```\n \n  ### Readability Scores\n \n  Readability is the ease with which a reader can understand a written\n text. In natural language, the readability of text depends on its\n content (the complexity of its vocabulary and syntax) and its\n presentation (such as typographic aspects like font size, line height,\n and line length).\n \n  #### Popular Metrics\n \n  -   The Flesch formulas\n     :   -   Flesch-Kincaid Readability Score\n         -   Flesch-Kincaid Reading Ease\n \n  -   Dale-Chall formula\n -   SMOG\n -   Coleman-Liau Index\n -   Automated Readability Index\n -   FORCAST\n \n  [For more in depth reading.](https://en.wikipedia.org/wiki/Readability)\n\nContributing\n============\n\n#### Setup\n1. Install [Poetry](https://poetry.eustace.io/)\n1. Run `make setup` to prepare workspace\n\n#### Testing\n1. Run `make test` to run all tests\n\n#### Linting\n1. Run `make format` to run black code formatter\n1. Run `make lint` to run pylint\n1. Run `make mypy` to run mypy',
    'author': 'Michael Holtzscher',
    'author_email': 'mholtz@protonmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
