import sqlalchemy as sa

from ..config import Base



class ModelInvalidFieldNames(Base):
    __tablename__ = 'model_invalid_field_names'
    
    id = sa.Column(sa.Integer, primary_key=True)
    f__integer = sa.Column(sa.Integer)