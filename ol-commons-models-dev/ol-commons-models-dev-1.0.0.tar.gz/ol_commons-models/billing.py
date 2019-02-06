from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
base = declarative_base()


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    sq_pchorder_id = Sequence('sq_pchorder_id', metadata=base.metadata)

    num_pchorder_id = db.Column(db.Numeric,
                                sq_pchorder_id,
                                server_default=sq_pchorder_id.next_value(),
                                primary_key=True)

    str_pchorder_code = db.Column(db.Text)
    num_pchorder_status = db.Column(db.Numeric)
    str_modifiedby = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    dte_modifieddate = db.Column(db.DateTime)
