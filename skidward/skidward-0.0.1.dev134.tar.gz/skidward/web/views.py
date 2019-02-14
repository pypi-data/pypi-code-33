from wtforms.fields import PasswordField

from flask import redirect, url_for, render_template
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_security import login_required, current_user, login_user, logout_user, utils


class UserAdmin(ModelView):
    form_excluded_columns = ("password",)

    def is_accessible(self):
        return current_user.has_role("admin")

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password2 = PasswordField("New Password")
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = utils.hash_password(model.password2)


class RoleAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role("admin")


class SkidwardView(AdminIndexView):
    @expose("/")
    @login_required
    def index(self):
        return render_template("index.html")

    @expose("/login")
    def login(self):
        login_user(current_user)
        return redirect(url_for("admin.index"))

    @expose("/logout")
    def logout(self):
        logout_user()
        return redirect(url_for("index"))
