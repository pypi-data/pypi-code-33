# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sqla_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['inflection', 'sqlalchemy>=1.0,<2.0']

setup_kwargs = {
    'name': 'sqla-wrapper',
    'version': '2.0.1',
    'description': 'A framework-independent wrapper for SQLAlchemy that makes it really easy to use.',
    'long_description': "===========================\nSQLA-wrapper |travis|\n===========================\n\n.. |travis| image:: https://travis-ci.org/jpscaletti/sqla-wrapper.png\n   :alt: Build Status\n   :target: https://travis-ci.org/jpscaletti/sqla-wrapper\n\nA friendly wrapper for SQLAlchemy.\n\n.. sourcecode:: python\n\n    from sqla_wrapper import SQLAlchemy\n\n    db = SQLAlchemy('sqlite:///:memory:')\n\n    class ToDo(db.Model):\n        id = db.Column(db.Integer, primary_key=True)\n        ...\n\n    db.create_all()\n    \n    db.add(Todo(...))\n    db.commit()\n\n    # Sorry, we don't support the `Model.query` syntax\n    todos = db.query(ToDo).all()\n\n\nRead the complete documentation here: https://jpscaletti.com/sqla-wrapper\n\nSince 2.0, only Python 3.6 or later are supported.\nPlease use the `1.9.1` version if your project runs on a previous Python version.\n\nSQLAlchemy\n======================\n\nThe things you need to know compared to plain SQLAlchemy are:\n\n1.  The ``SQLAlchemy`` gives you access to the following things:\n\n    -   All the functions and classes from ``sqlalchemy`` and\n        ``sqlalchemy.orm``\n    -   All the functions from a preconfigured scoped session (called ``_session``).\n    -   The ``~SQLAlchemy.metadata`` and ``~SQLAlchemy.engine``\n    -   The methods ``SQLAlchemy.create_all`` and ``SQLAlchemy.drop_all``\n        to create and drop tables according to the models.\n    -   a ``Model`` baseclass that is a configured declarative base.\n\n2.  All the functions from the session are available directly in the class, so you\n    can do ``db.add``,  ``db.commit``,  ``db.remove``, etc.\n\n3.  The ``Model`` declarative base class behaves like a regular\n    Python class but has a ``query`` attribute attached that can be used to\n    query the model.\n\n4.  The ``Model`` class also auto generates ``_tablename__`` attributes, if you\n    don't define one, based on the underscored and **pluralized** name of your classes.\n\n5.  You have to commit the session and configure your app to remove it at\n    the end of the request.\n\n\nRun the tests\n======================\n\nYou'll need `poetry` to install de development dependencies.\n\n  poetry install\n\nThis command will automnatically create a virtual environment to run the project in.\nRead more in the `Poetry site <https://poetry.eustace.io/>`_\n\nTo run the tests in your current Python version do::\n\n    pytest tests\n\nTo run them in every supported Python version do::\n\n    tox\n\nIt's also neccesary to run the coverage report to make sure all lines of code\nare touch by the tests::\n\n    make coverage\n\nOur test suite `runs continuously on Travis CI <https://travis-ci.org/jpscaletti/sqla-wrapper>`_ with every update.\n\n\n:copyright: 2013-2019 by `Juan-Pablo Scaletti <http://jpscaletti.com>`_.\n:license: MIT, see LICENSE for more details.\n",
    'author': 'Juan-Pablo Scaletti',
    'author_email': 'juanpablo@jpscaletti.com',
    'url': 'https://jpscaletti.com/sqla-wrapper/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
