import logging
import os
import pickle

from django.apps import apps
from django.conf import settings
from sqlalchemy import ColumnDefault
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.pool import NullPool


logger = logging.getLogger(__name__)


class ClassNotFoundError(Exception):
    pass

def sqlite_connection_string(db_path):
    # Call normpath to ensure that Windows paths are properly formatted
    return 'sqlite:///{db_path}'.format(db_path=os.path.normpath(db_path))

def get_engine(connection_string):
    """
    Get a SQLAlchemy engine that allows us to connect to a database.
    """
    # Set echo to False, as otherwise we get full SQL Query outputted, which can overwhelm the terminal
    engine = create_engine(
        connection_string,
        echo=False,
        connect_args={'check_same_thread': False} if connection_string.startswith('sqlite') else {},
        poolclass=NullPool,
        convert_unicode=True,
    )
    return engine

def get_class(DjangoModel, Base):
    """
    Given a DjangoModel and SQLAlachemy Base mapping that has undergone reflection to have
    SQLAlchemy ORM classes that reflect the current state of the database, return the relevant
    Base class for the passed in DjangoModel class definition
    """
    try:
        # The classes are named, by default, with the name of the table they reflect
        # Use the DjangoModel's _meta db_table attribute to look up the class
        return Base.classes[DjangoModel._meta.db_table]
    except KeyError:
        raise ClassNotFoundError('No SQL Alchemy ORM Mapping for this Django model found in this database')

def set_all_class_defaults(Base):
    """
    Django model fields can have defaults. Unfortunately, these defaults are only set in Python
    not on the database itself, therefore, if we want to use SQLAlchemy to create records in the database
    table, while adhering to these Django field defaults, we have to set them up again on the SQLAlchemy
    class, this method does that to all the classes defined on the passed in Base mapping.
    """
    for DjangoModel in apps.get_models():
        # Iterate through all the Django Models defined
        try:
            # Try to get a class that corresponds to this model
            # This might not exist because we only did a reflection restricted to a few tables, or
            # because we have a database table not reflected in our Django models.
            BaseClass = get_class(DjangoModel, Base)
            for field in DjangoModel._meta.fields:
                # If we do have valid class, we can iterate through the fields and find all the fields that
                # have defaults
                if field.has_default():
                    column = BaseClass.__table__.columns.get(field.attname)
                    # If there are schema differences between the Django model and the particular table
                    # that we are looking at (even though it has the same table name), then the column
                    # with a default value may not exist
                    if column is not None:
                        # The column does exist, set up a default by creating a SQLALchemy ColumnDefault object
                        default = ColumnDefault(field.default)
                        # Set the default of this column to our new default
                        column.default = default
                        # This is necessary, but I can't find the part of the SQLAlchemy source code that
                        # I found this.
                        default._set_parent_with_dispatch(column)
        except ClassNotFoundError:
            pass

def prepare_base(engine):
    """
    Create a Base mapping for models for a particular schema version of the content app
    A Base mapping defines the mapping from database tables to the SQLAlchemy ORM and is
    our main entrypoint for interacting with content databases and the content app tables
    of the default database.
    """
    # Set up the base mapping using the automap_base method
    Base = automap_base()
    # TODO map relationship backreferences using the django names
    # Calling Base.prepare() means that Base now has SQLALchemy ORM classes corresponding to
    # every database table that we need
    Base.prepare(engine, reflect=True)
    # Set any Django Model defaults
    set_all_class_defaults(Base)
    return Base

def get_default_db_string():
    """
    Function to construct a SQLAlchemy database connection string from Django DATABASE settings
    for the default database
    """
    destination_db = settings.DATABASES.get('default')
    if 'sqlite' in destination_db['ENGINE']:
        return sqlite_connection_string(destination_db['NAME'])
    else:
        return '{dialect}://{user}:{password}@{host}{port}/{dbname}'.format(
            dialect=destination_db['ENGINE'].split('.')[-1],
            user=destination_db['USER'],
            password=destination_db['PASSWORD'],
            host=destination_db.get('HOST', 'localhost'),
            port=':' + destination_db.get('PORT') if destination_db.get('PORT') else '',
            dbname=destination_db['NAME'],
        )


class Bridge(object):

    def __init__(self, sqlite_file_path=None):
        self.connection_string = get_default_db_string()
        self.engine = get_engine(self.connection_string)
        self.Base = prepare_base(self.engine)

        self.connections = []

    def get_class(self, DjangoModel):
        return get_class(DjangoModel, self.Base)

    def get_table(self, DjangoModel):
        return self.get_class(DjangoModel).__table__

    def get_connection(self):
        connection = self.engine.connect()
        self.connections.append(connection)
        return connection

    def end(self):
        for connection in self.connections:
            connection.close()
