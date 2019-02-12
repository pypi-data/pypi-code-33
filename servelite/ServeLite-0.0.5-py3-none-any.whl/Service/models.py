from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.types import  String, Text, TIMESTAMP, Integer
from sqlalchemy.orm import  relationship, sessionmaker

from .config import used_config

engine = create_engine(used_config['uri'])
Base = declarative_base(engine)
session = sessionmaker(engine)

def get_session():
    return session()

class Tables(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True)
    fields = relationship('Fields', backref='tables')
    sensitivity = Column(Integer)
    register_time = Column(TIMESTAMP)
    register_info = Column(Text)

class Fields(Base):
    __tablename__ = 'fields'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey(Tables.id))
    name = Column(String(64))
    sensitivity = Column(Integer)

class APIs(Base):
    __tablename__ = 'apis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule = Column(String(256))
    name = Column(String(64)) # API名称
    description = Column(String(256)) # 描述
    sensitivity = Column(Integer)
    type = Column(String(64)) # 类型
    status = Column(Integer) # 0 未注册 1 已注册

    def info(self):
        s = {}
        ex = ['metadata']
        for i in self.__dir__():
            if i[:1] != '_' and i[-1:] != '_'\
                    and i not in ex \
                    and not hasattr(self.__getattribute__(i), '__call__'):
                s[i] = self.__getattribute__(i)
        return s



def create():
    Base.metadata.create_all()

if __name__ == '__main__':
    meta = Base.metadata
    a=1