"""
    forms of Lin
    ~~~~~~~~~

    forms check the incoming params and data

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import request
from wtforms import Form as WTForm

from .exception import ParameterException


class Form(WTForm):
    def __init__(self):
        data = request.get_json(silent=True)
        args = request.args.to_dict()
        super(Form, self).__init__(data=data, **args)

    def validate_for_api(self):
        valid = super(Form, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self
