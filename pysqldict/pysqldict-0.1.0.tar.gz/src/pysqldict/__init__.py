from .sqldict import SqlDict

__version__ = '0.1.0'


def open(filename=':memory:'):
    """Opens a SQLite database file. Returns a database object that can be used to
    retrieve tables.

    :param filename: Path of the database file. Use memory database (`:memory:`) if omitted.
    :rtype: Database object.
    """
    return SqlDict(filename)
