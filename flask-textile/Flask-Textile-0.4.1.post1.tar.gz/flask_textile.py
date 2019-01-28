from flask import Markup
from textile import textile as parser

class Textile:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.filters['textile'] = self.markup

    @classmethod
    def markup(cls, text):
        return Markup(cls.parse(text))

    @staticmethod
    def parse(text):
        return parser(text).strip()
