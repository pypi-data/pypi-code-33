from setuptools import setup, find_packages

version = '1.3'
maintainer = 'Julian Infanger'

tests_require = ['plone.app.testing',
                 'ftw.builder',
                 'ftw.testbrowser',
                 'ftw.testing',
                 'unittest2',
                 'plone.app.event',
                 'ftw.events [tests]',
                 ]

setup(name='ftw.calendarexport',
      version=version,
      description="Export function for ftw.calendar (Maintainer: %s)" % maintainer,
      long_description=open("README.rst").read() + "\n" + \
          open("docs/HISTORY.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://github.com/4teamwork/ftw.calendarexport',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      install_requires=[
        'Plone',
        'setuptools',
        'ftw.calendar',
        'ftw.calendarwidget',
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
