from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, LargeBinary


Base = declarative_base()


class SoupstarsCache(Base):
    __tablename__ = "soupstars_cache"
    id = Column(String(80), primary_key=True)
    blob = Column(LargeBinary, nullable=False)
