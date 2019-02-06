from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
base = declarative_base()


class Attribute(db.Model):
    __tablename__ = 'attribute'
    sq_attribute_id = Sequence('sq_attribute_id', metadata=base.metadata)

    num_attribute_id = db.Column(db.Numeric, sq_attribute_id, server_default=sq_attribute_id.next_value(),
                                 primary_key=True)
    str_attribute_name = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_attribute_desc = db.Column(db.Text)


class AttributeMember(db.Model):
    __tablename__ = 'attribute_member'

    sq_attribute_member_id = Sequence('sq_attribute_member_id', metadata=base.metadata)
    num_attr_member_id = db.Column(db.Numeric, sq_attribute_member_id,
                                   server_default=sq_attribute_member_id.next_value(), primary_key=True)

    num_attribute_id = db.Column(db.Numeric)
    str_attr_member_value = db.Column(db.Text)
    str_attr_member_desc = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    num_order = db.Column(db.Numeric)
    str_attr_member_desc_2 = db.Column(db.Text)
