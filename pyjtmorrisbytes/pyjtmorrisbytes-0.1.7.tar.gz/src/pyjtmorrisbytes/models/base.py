"""
 commonmodels:
 the library that holds base classes used with 
 sqlalchemy across all applications

"""

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, Unicode, DateTime
import string
import uuid
import datetime
import cython

from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID




class Base(object):
    # common variables used everywhere
    uuid_size: cython.int = 36
    uuid_valid_characters: cython.char = string.ascii_letters + string.digits + '-'
    
    @cython.returns(str)
    @declared_attr
    def __tablename__(self, cls):
        return cls.__name__.lower()
    id = Column(Integer(), primary_key=True)
    uuid = Column(Unicode(uuid_size), unique=True, default=str(uuid.uuid4()),
                  nullable=False)
    createdon = Column(DateTime(), default=datetime.datetime.now())
    lastupdated = Column(DateTime(), default=datetime.datetime.now,
                         onupdate=datetime.datetime.now)

    @cython.returns(str)
    def __repr__(self):
        representation: str = '< ' + self.__class__.__name__ + '() '
        for attr, value in self.__dict__.items():
            representation += ' ' + attr, ': ' + value + ', '
        representation += ')>'
        return representation
