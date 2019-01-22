ADAPTERS = []  # list of all loaded adapters
"""
When loading an adapter we have to first check if necessary requirements are
met (if particular ORM library is installed), only then we can import
adapter. Otherwise `ImportError` maybe a result of not ORM being not
installed, but actual error in an adapter.
"""

#--- SQL Alchemy ---------------------------------------------------------------
__requirements_installed = False
try:
    import sqlalchemy
    __requirements_installed = True
except ImportError:
    pass

if __requirements_installed:
    from .sqlalchemy_adapter import SqlachemyAdapter
    ADAPTERS.append(SqlachemyAdapter)

#--- Django ORM ----------------------------------------------------------------
__requirements_installed = False
try:
    import django
    __requirements_installed = True
except ImportError:
    pass

if __requirements_installed:
    from .django_adapter import DjangoAdapter
    ADAPTERS.append(DjangoAdapter)

#-------------------------------------------------------------------------------


