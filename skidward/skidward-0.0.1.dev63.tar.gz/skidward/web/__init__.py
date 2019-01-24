from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, utils
import click
from flask.cli import AppGroup


# Initializing the Flask App
from werkzeug.local import LocalProxy

app = Flask(__name__)

user_cli = AppGroup('user')

# Import all Models and database object after creation of app
from skidward.web.models import db, User, Role, Worker, UserAdmin, RoleAdmin

# Setting any FLASK_ADMIN_SWATCH(Theme Template)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# Setting up Postgres Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:abs0701@localhost/skidwardDB'

# Setting up a secret key
app.config['SECRET_KEY'] = b"\x0bH\xd4\x03\x91\x89Z\xc3j\xf9M\x81&\xbe#'"
app.config['SECURITY_PASSWORD_SALT'] = b"\x0bH\xd4\x03\x91\x89Z\xc3j\xf9M\x81&\xbe#'"
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'

app.debug = True

# Initializing admin with flask app, name and template type
admin = Admin(app, name='Skidward-Admin', template_mode='bootstrap3')


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@user_cli.command('create')
@click.argument('email')
def superuser(email):
    password = utils.hash_password(
        click.prompt(
            'Please enter your password',
            hide_input=True,
            confirmation_prompt=True
        )
    )
    db.create_all()
    user_datastore.find_or_create_role(name="admin", description='Administrator')
    user_datastore.find_or_create_role(name='end-user', description='End user')
    db.session.commit()

    _datastore = LocalProxy(lambda: app.extensions['security'].datastore)

    admin = _datastore.create_user(
        email=email,
        username=email.split("@")[0],
        password=password,
    )
    user_datastore.add_role_to_user(email, 'admin')
    db.session.commit()
    click.echo("Superuser is Created")


# Adding Models as Views to admin
admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))
admin.add_view(ModelView(Worker, db.session))


import skidward.web.views

app.cli.add_command(user_cli)

if __name__ == "__main__":
    app.run()

