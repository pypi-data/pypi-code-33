import dredd_hooks as hooks

import sys
import os.path as path
import requests
from flask import Flask

# DO NOT REMOVE THIS. This adds the project root for successful imports. Imports from the project directory should be
# placed only below this
sys.path.insert(1, path.abspath(path.join(__file__, "../..")))

from mixer.backend.flask import mixer

from app.models import db
from geokrety_api_models import (Geokret, News, NewsComment, NewsSubscription,
                                 User)


stash = {}
api_username = "someone"
api_password = "strong password"
api_uri = "http://localhost:5002/auth/session"


def obtain_token():
    data = {
        "username": api_username,
        "password": api_password
    }
    url = api_uri
    response = requests.post(url, json=data)
    response.raise_for_status()
    parsed_body = response.json()
    token = parsed_body["access_token"]
    return token


@hooks.before_all
def before_all(transaction):
    app = Flask(__name__)
    app.config.from_object('config.TestingConfig')
    db.init_app(app)

    stash['app'] = app
    stash['db'] = db


@hooks.before_each
def before_each(transaction):
    with stash['app'].app_context():
        db.engine.execute("drop database geokrety_unittest")
        db.engine.execute("create database geokrety_unittest")
        db.engine.execute("use geokrety_unittest")
        db.create_all()

        with stash['app'].test_request_context():
            mixer.init_app(stash['app'])
            with mixer.ctx(commit=False):
                user_1 = mixer.blend(User, name=api_username)
                user_1.password = api_password
                user_2 = mixer.blend(User)

                news_1 = mixer.blend(News, author=user_1)
                news_2 = mixer.blend(News, author=None)
                news_comment = mixer.blend(NewsComment, author=user_1, news=news_1)
                new_subscription1 = mixer.blend(NewsSubscription, user=user_1, news=news_1)

                geokret_1 = mixer.blend(Geokret)

        db.session.add(user_1)
        db.session.add(user_2)
        db.session.add(news_1)
        db.session.add(news_2)
        db.session.add(news_comment)
        db.session.add(new_subscription1)
        db.session.add(geokret_1)
        db.session.commit()

    if 'token' not in stash:
        stash['token'] = obtain_token()

    transaction['request']['headers']['Authorization'] = "JWT " + stash['token']


@hooks.after_each
def after_each(transaction):
    with stash['app'].app_context():
        db.session.remove()
