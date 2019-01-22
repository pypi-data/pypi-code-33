# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['pdftxt']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0', 'pdfminer.six>=20181108.0,<20181109.0']

entry_points = \
{'console_scripts': ['pdftxt = pdftxt.cli:main']}

setup_kwargs = {
    'name': 'pdftxt',
    'version': '0.2.0',
    'description': 'PDF text extractor.',
    'long_description': "### pdftxt\n\nThe goal of this project is to provide an api to extract text\nfrom specific regions of a pdf document/page and a cli to assist\nidentifying the location of text within a document.\n\n### Installation\n\n\n    ... pip install pdftxt\n\n\n### Basic Command Line Usage\n\nLet's say we have a PDF file (PDF-DOC.pdf) that looks like this:\n\n![Source File Image](https://bytebucket.org/mgemmill/pdftxt/raw/36ef6c80f953ac5d4eae712d5c7943c23e8914bc/assets/readme_src_doc_.jpg)\n\nThe `pdftxt` command:\n\n    ... pdft PDF-DOC.pdf\n\nWill output a visual layout of the pdf document's pages and text elements to an html page:\n\n![Output File Image](https://bytebucket.org/mgemmill/pdftxt/raw/36ef6c80f953ac5d4eae712d5c7943c23e8914bc/assets/readme_output_doc_.jpg)\n\n\n### Basic API Usage\n\n\n    from pathlib import Path\n    from pdftxt import api\n\n    filepath = 'tests/Word_PDF.pdf'\n\n    with api.PdfTxtContext(filepath) as pdf:\n\n        for page in pdf:\n\n            # To fetch text objects from specific region\n            # of the page, first define the region:\n            region = api.Region(400, 300, 512, 317)\n\n            # Initialize layout parameters:\n            params = api.PdfTxtParams()\n\n            # Then analyze that area of the page for text objects:\n            text = page.analyze(region, params)\n\n            # Do whatever it is we need to do with the results:\n            for txt in text:\n                print(txt.text)\n",
    'author': 'Mark Gemmill',
    'author_email': 'bitbucket@markgemmill.com',
    'url': 'https://bitbucket.org/mgemmill/pdftxt',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
