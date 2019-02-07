# pylint: disable=W0622
"""cubicweb-celery application packaging information"""


modname = 'cubicweb_celery'
distname = 'cubicweb-celery'

numversion = (0, 4, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'Christophe de Vienne'
author_email = 'christophe@unlish.com'
description = 'Celery cube'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.24',
    'six': '>= 1.4.0',
    'celery': '>=4,<5',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
