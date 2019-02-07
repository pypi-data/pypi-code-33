# pylint: disable=W0622
"""cubicweb-rqlcontroller application packaging information"""

modname = 'rqlcontroller'
distname = 'cubicweb-rqlcontroller'

numversion = (0, 5, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'restfull rql edition capabilities'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.25.0',
    'six': None,
}
__recommends__ = {'cubicweb-signedrequest': None}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
