import os
from . import PGPString
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
base = declarative_base()


class User(db.Model):
    __tablename__ = 'user'

    sq_user_id = Sequence('sq_user_id', metadata=base.metadata)
    num_user_id = db.Column(db.Numeric, sq_user_id, server_default=sq_user_id.next_value(),
                            primary_key=True)
    str_user_name = db.Column(db.Text)
    str_user_password = db.Column(PGPString(os.environ.get('DBARTEMISKEY'), length=1000))
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Application(db.Model):
    __tablename__ = 'application'

    num_application_id = db.Column(db.Numeric, primary_key=True)
    str_application_name = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)


class AuthorizedCryptUser(db.Model):
    __tablename__ = 'authorized_crypt_user'

    num_user_id = db.Column(db.Numeric)
    num_crypc_id = db.Column(db.Numeric)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class EncryptTables(db.Model):
    __tablename__ = 'encrypt_tables'
    sq_encrypt_id = Sequence('sq_encrypt_id',
                             metadata=base.metadata)

    num_encryp_id = db.Column(db.Numeric,
                              sq_encrypt_id,
                              server_default=sq_encrypt_id.next_value(),
                              primary_key=True)

    num_user_id = db.Column(db.Numeric)
    str_schema_name = db.Column(db.Text)
    str_table_name = db.Column(db.Text)
    str_encrypt_status = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)


class EncryptedColumns(db.Model):
    __tablename__ = 'encrypted_columns'

    num_crypc_id = db.Column(db.Numeric, primary_key=True)
    str_schema_name = db.Column(db.Text)
    str_table_name = db.Column(db.Text)
    str_column_name = db.Column(db.Text)
    str_password_for_crypt = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Module(db.Model):
    __tablename__ = 'module'

    str_module_id = db.Column(db.Text, primary_key=True)
    str_module_name = db.Column(db.Text)
    str_module_des = db.Column(db.Text)
    num_order = db.Column(db.Numeric)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    num_application_id = db.Column(db.Numeric)
    str_icon = db.Column(db.Text)


class SubModule(db.Model):
    __tablename__ = 'submodule'

    str_submodule_id = db.Column(db.Text, primary_key=True)
    str_submodule_name = db.Column(db.Text)
    str_submodule_des = db.Column(db.Text)
    str_module_id = db.Column(db.Text, db.ForeignKey('module.str_module_id'), nullable=False)
    str_submodule_title = db.Column(db.Text)
    num_order = db.Column(db.Numeric)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_action = db.Column(db.Text)


class OauthCredentials(db.Model):
    __tablename__ = 'oauth_credentials'

    num_oauth_cred_id = db.Column(db.Numeric, primary_key=True)

    str_oauth_cred_user = db.Column(db.Text)
    str_oauth_cred_password = db.Column(db.Text)

    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Role(db.Model):
    __tablename__ = 'role'

    str_role_id = db.Column(db.Text, primary_key=True)
    str_role_name = db.Column(db.Text)
    str_rol_des = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class RoleSubModule(db.Model):
    __tablename__ = 'role_submodule'

    str_submodule_id = db.Column(db.Text, db.ForeignKey('submodule.str_submodule_id'), nullable=False, primary_key=True)
    str_role_id = db.Column(db.Text, db.ForeignKey('role.str_role_id'), nullable=False)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Session(db.Model):
    __tablename__ = 'session'
    sq_session_id = db.Column('sq_session_id',
                              metadata=base.metadata)

    num_session_id = db.Column(db.Numeric,
                               sq_session_id,
                               server_default=sq_session_id.next_value(),
                               primary_key=True)

    num_user_id = db.Column(db.Numeric, db.ForeignKey('user.num_user_id'), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_state = db.Column(db.Text)


class UserRole(db.Model):
    __tablename__ = 'user_role'

    str_role_id = db.Column(db.Text, db.ForeignKey('role.str_role_id'), nullable=False, primary_key=True)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    num_user_id = db.Column(db.Numeric, db.ForeignKey('user.num_user_id'), nullable=False)
