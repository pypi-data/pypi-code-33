# pylint: disable=W0622
"""cubicweb-celerytask application packaging information"""


modname = 'cubicweb_celerytask'
distname = 'cubicweb-celerytask'

numversion = (0, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Run and monitor celery tasks'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.19',
    'six': '>= 1.4.0',
    'celery': '>=4,<5',
    'cw-celerytask-helpers': '>= 0.7.0, < 0.8.0',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
