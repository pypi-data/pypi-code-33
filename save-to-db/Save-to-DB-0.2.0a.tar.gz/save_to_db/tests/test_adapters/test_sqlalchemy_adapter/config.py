from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///:memory:', echo=False)
# engine = create_engine('sqlite:///db.sqlite', echo=False)
Base = declarative_base()

DBSession = sessionmaker(bind=engine)
session = DBSession()