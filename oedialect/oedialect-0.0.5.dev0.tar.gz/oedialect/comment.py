from sqlalchemy import *
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_comment_table(schema, table_name, metadata):
    class CommentTable(Base):
        __tablename__ = '_{table}_cor'.format(schema=schema,table=table_name)
        __table_args__ = {"schema": schema}
        id = Column('id', BigInteger, primary_key=True)
        origin = Column('origin', String(2000))
        method = Column('method', String(3000))
        assumptions = Column('assumption', JSON, nullable=True)
    return CommentTable