from skidward.web import app
from flask import redirect, url_for, render_template
from flask_security import (login_required, current_user,
                            login_user, logout_user,
                            registerable)


# Creating routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    registerable.register_user()
    login_user()
    redirect(url_for('index.html'))


@app.route('/login')
def login():
    login_user(current_user)


@app.route('/logout')
def logout():
    logout_user(current_user)
    return redirect(url_for('index.html'))

