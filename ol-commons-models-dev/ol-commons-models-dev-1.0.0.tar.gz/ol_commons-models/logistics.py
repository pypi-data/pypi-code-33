from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
base = declarative_base()


class Assets(db.Model):
    __tablename__ = 'assets'
    sq_assets_id = Sequence('sq_assets_id', metadata=base.metadata)

    num_assets_id = db.Column(db.Numeric,
                              sq_assets_id,
                              server_default=sq_assets_id.next_value(),
                              primary_key=True)

    str_assets_name = db.Column(db.Text)
    str_trademark = db.Column(db.Text)
    dte_acquisitiondate = db.Column(db.DateTime)
    chr_state = db.Column(db.Text)
    str_sighting = db.Column(db.Text)
    str_assets_id = db.Column(db.Text)
    chr_availability = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    dte_modifieddate = db.Column(db.DateTime)


class AssetsMovements(db.Model):
    __tablename__ = ' assets_movements'
    sq_assets_movements_id = Sequence('sq_assets_movements_id', metadata=base.metadata)

    num_assets_movements_id = db.Column(db.Numeric,
                                        sq_assets_movements_id,
                                        server_default=sq_assets_movements_id.next_value(),
                                        primary_key=True)

    num_assets_id = db.Column(db.Numeric)
    dte_assetsmovements_date = db.Column(db.DateTime)
    num_units = db.Column(db.Numeric)
    dte_execution = db.Column(db.DateTime)
    str_reason = db.Column(db.Text)
    str_type = db.Column(db.Text)
    str_function = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Allocation(db.Model):
    __tablename__ = 'allocation'

    num_allocation_id = db.Column(db.Numeric,
                                  primary_key=True)

    num_employee_id = db.Column(db.Numeric)
    str_state_allocation = db.Column(db.Text)
    str_confirmation_flag = db.Column(db.Text)
    str_reason = db.Column(db.Text)
    dte_order = db.Column(db.DateTime)
    dte_reception = db.Column(db.DateTime)
    dte_createddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)


class AssetsDetail(db.Model):
    __tablename__ = 'assets_detail'

    num_assets_id = db.Column(db.Numeric,
                              primary_key=True)

    num_feature_assets_id = db.Column(db.Numeric)
    str_description = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)


class AssetsFeature(db.Model):
    __tablename__ = 'assets_feature'
    sq_assets_feature_id = db.Column('sq_assets_feature_id', metadata=base.metadata)

    num_assets_feature_id = db.Column(db.Numeric,
                                      sq_assets_feature_id,
                                      server_default=sq_assets_feature_id.next_value(),
                                      primary_key=True)

    str_feature_name = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)


class AssetsType(db.Model):
    __tablename__ = 'assets_type'
    sq_assets_type_id = db.Column('sq_assets_type _id', metadata=base.metadata)

    num_assets_type_id = db.Column(db.Numeric,
                                   sq_assets_type_id,
                                   server_default=sq_assets_type_id.next_value(),
                                   primary_key=True)

    str_type_name = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class AssetsTickets(db.Model):
    __tablename__ = 'assets_tickets'
    sq_assets_tickets_id = db.Column('sq_assets_tickets_id',
                                     metadata=base.metadata)

    num_assets_tickets_id = db.Column(db.Numeric,
                                      sq_assets_tickets_id,
                                      server_default=sq_assets_tickets_id.next_value(),
                                      primary_key=True)

    str_description = db.Column(db.Text)
    str_solution = db.Column(db.Text)
    dte_opening_date = db.Column(db.DateTime)
    dte_closing_date = db.Column(db.DateTime)
    str_state = db.Column(db.Text)
    num_assets_id = db.Column(db.Numeric)
    dte_createddate = db.Column(db.DateTime)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)


class AssetsTypeFeature(db.Model):
    __tablename__ = 'assets_type_feature'

    num_type_id = db.Column(db.Numeric)
    num_feature_id = db.Column(db.Numeric)
    dte_createddate = db.Column(db.DateTime)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
