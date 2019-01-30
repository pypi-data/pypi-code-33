from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
from . conf import Config


Base = declarative_base()
config = Config()


class Url(Base):
    __tablename__ = 'url'
    url_id = Column(Integer, primary_key=True)
    domain_name = Column(String(250), unique=True)
    time_stamp = Column(DateTime, default=datetime.now)


class Subject(Base):
    __tablename__ = 'subject'
    subject_id = Column(Integer, primary_key=True)
    subject_name = Column(String(250), nullable=False)
    directory_name = Column(String(250), nullable=False, unique=True)
    time_stamp = Column(DateTime, default=datetime.now)


class PathType(Base):
    __tablename__ = 'path_type'
    path_type_id = Column(Integer, primary_key=True)
    path_type = Column(String(250), unique=True)
    time_stamp = Column(DateTime, default=datetime.now)


class Path(Base):
    __tablename__ = 'path'
    path_id = Column(Integer, primary_key=True)
    path = Column(String(250), unique=True)
    year = Column(Integer)
    url_id = Column(Integer, ForeignKey('url.url_id'))
    url = relationship(Url)
    subject_id = Column(Integer, ForeignKey('subject.subject_id'))
    subject = relationship(Subject)
    path_type_id = Column(Integer, ForeignKey('path_type.path_type_id'))
    path_type = relationship(PathType)
    time_stamp = Column(DateTime, default=datetime.now)


engine = create_engine('sqlite:///' + config.db_dir + '/fec.db')
Base.metadata.create_all(engine)
