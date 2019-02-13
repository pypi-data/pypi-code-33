# pylint: disable-msg=W0622
"""cubicweb-card application packaging information"""

modname = 'cubicweb_card'
distname = 'cubicweb-card'

numversion = (1, 0, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
web = 'http://www.cubicweb.org/project/%s' % distname
description = 'card/wiki component for the CubicWeb framework'
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
]

__depends__ = {
    'cubicweb': '>= 3.24',
    'docutils': None,
    }
__recommends__ = {
    'cubicweb-preview': None,
    'cubicweb-seo': None,
    }
