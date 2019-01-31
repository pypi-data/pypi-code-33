from d3m.metadata import base as meta_base

D3M_API_VERSION = '2019.1.21'
VERSION = '1.2.1'
TAG_NAME = ''

REPOSITORY = 'https://gitlab.datadrivendiscovery.org/dhartnett/psl'
ISSUES_URL = 'https://gitlab.datadrivendiscovery.org/dhartnett/psl/issues'
PACKAGE_NAME = 'sri-d3m'

D3M_PERFORMER_TEAM = 'SRI'
MAINTAINER = 'Eriq Augustine'
EMAIL = 'eaugusti@ucsc.edu'

PACKAGE_URI = ''
if TAG_NAME:
    PACKAGE_URI = "git+%s@%s" % (REPOSITORY, TAG_NAME)
else:
    PACKAGE_URI = "git+%s" % (REPOSITORY)

PACKAGE_URI = "%s#egg=%s" % (PACKAGE_URI, PACKAGE_NAME)

INSTALLATION = {
    'type' : meta_base.PrimitiveInstallationType.PIP,
    'package': PACKAGE_NAME,
    'version': VERSION
}

INSTALLATION_JAVA = {
    'type' : meta_base.PrimitiveInstallationType.UBUNTU,
    'package': 'default-jre',
    'version': '2:1.8-56ubuntu2'
}

INSTALLATION_POSTGRES = {
    'type' : meta_base.PrimitiveInstallationType.UBUNTU,
    'package': 'postgresql',
    'version': '9.5+173ubuntu0.1'
}

SOURCE = {
    'name': D3M_PERFORMER_TEAM,
    'uris': [ REPOSITORY, ISSUES_URL ],
    'contact': "mailto:%s" % (EMAIL),
}
