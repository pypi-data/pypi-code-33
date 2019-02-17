import click
import os
from werkzeug.local import LocalProxy


from flask import Flask
from flask.cli import AppGroup
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, utils


# Initializing the Flask App
app = Flask(__name__)

user_cli = AppGroup("user")

# Import all Models and database object after creation of app
from skidward.models import db, User, Role, Worker, Task, Job
from skidward.web.views import SkidwardView, UserAdmin, RoleAdmin

# Setting any FLASK_ADMIN_SWATCH(Theme Template)
app.config["FLASK_ADMIN_SWATCH"] = os.getenv("FLASK_ADMIN_SWATCH")

# Setting up Postgres Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

# Setting up a secret key
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")
app.config["SECURITY_PASSWORD_HASH"] = os.getenv("SECURITY_PASSWORD_HASH")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
    "SQLALCHEMY_TRACK_MODIFICATIONS"
)

app.debug = True

# Initializing admin with flask app, name and template type
admin = Admin(app, name="Skidward-Admin", template_mode="bootstrap3")


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@user_cli.command("create")
@click.argument("email")
def superuser(email):
    password = utils.hash_password(
        click.prompt(
            "Please enter your password", hide_input=True, confirmation_prompt=True
        )
    )
    db.create_all()
    user_datastore.find_or_create_role(name="admin", description="Administrator")
    user_datastore.find_or_create_role(name="end-user", description="End user")
    db.session.commit()

    _datastore = LocalProxy(lambda: app.extensions["security"].datastore)

    admin = _datastore.create_user(
        email=email, username=email.split("@")[0], password=password
    )
    user_datastore.add_role_to_user(email, "admin")
    db.session.commit()
    click.echo("Superuser is Created")


# Adding Models as Views to admin
admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))
admin.add_view(ModelView(Worker, db.session))
admin.add_view(ModelView(Task, db.session))
admin.add_view(ModelView(Job, db.session))
admin = Admin(app, index_view=SkidwardView(endpoint="index", url="/", name="Home"))


app.cli.add_command(user_cli)

if __name__ == "__main__":
    app.run()
