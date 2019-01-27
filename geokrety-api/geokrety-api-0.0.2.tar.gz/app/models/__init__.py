# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

from geokrety_api_models.base import Base

db = SQLAlchemy(model_class=Base, session_options={"autoflush": False})
