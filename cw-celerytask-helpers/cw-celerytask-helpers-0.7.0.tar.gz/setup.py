import os.path
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
# load metadata from the __pkginfo__.py file so there is no risk of conflict
# see https://packaging.python.org/en/latest/single_source_version.html
pkginfo = os.path.join(here, 'cw_celerytask_helpers', '__pkginfo__.py')
__pkginfo__ = {'__file__': pkginfo}
with open(pkginfo) as f:
    exec(f.read(), __pkginfo__)

setup(
    name=__pkginfo__['distname'],
    version=__pkginfo__['version'],
    description=__pkginfo__['description'],
    author=__pkginfo__['author'],
    author_email=__pkginfo__['author_email'],
    license=__pkginfo__['license'],
    classifiers=__pkginfo__['classifiers'],
    packages=find_packages('.'),
    install_requires=["{0} {1}".format(d, v and v or "").strip()
                      for d, v in __pkginfo__['__depends__'].items()],
)
