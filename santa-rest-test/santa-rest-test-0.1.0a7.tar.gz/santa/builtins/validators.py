from jq import jq
import re

from santa.validator import Validator, ValidationError
from santa.parser import StringField, YamlField, ListField


class StatusValidator(Validator):
    """
    Validate the HTTP status.
    """
    __yaml_name__ = "status"
    expected = ListField(is_main=True)

    async def __call__(self, response, ctx):
        if response.status not in self.expected:
            raise ValidationError(
                "Response status, expected %s, got %s" % (
                    self.expected, response.status))


def dict_compare(model, data, path="", compare=None):
    for k in model:
        curpath = ".".join([path, k])
        if k not in data:
            raise ValidationError("Expected key `%s`" % curpath)
        else:
            curmodel = model[k]
            curdata = data[k]
            if type(curmodel) != type(curdata):
                raise ValidationError("Expected '%s' to be %s, got '%s'" % (
                    curpath, type(curmodel), type(curdata)))
            if isinstance(curmodel, dict):
                dict_compare(curmodel, curdata, curpath, compare)
            else:
                if compare:
                    compare(curmodel, curdata, curpath)
                elif curdata != curmodel:
                    raise ValidationError(
                            "Expected `%s` to be `%s`, got `%s`" % (
                                curpath, curmodel, curdata))


def match(model, data, path):
    if not re.match(model, data):
        raise ValidationError(
                "Expected `%s` to match `%s`, got `%s`" % (
                    path, model, data))


class Json(Validator):
    """
    Validate the JSON response against a set of rules.
    """
    pattern = StringField(help="jq search pattern.", default=".")
    equals = YamlField(help="The JSON value must be exactly this.",
                       default=None)
    partial = YamlField(help="Partial json validation, only fields present here are compared",
                        default=dict)
    partial_match = YamlField(help="Regular expressions that must match the data",
                              default=dict)
    contains = ListField(help="List of key path that must exist in the data",
                         default=list)

    async def __call__(self, response, ctx):
        data = jq(self.pattern).transform(await response.json())
        if self.equals is not None:
            expected = ctx.render(self.equals)
            if expected != data:
                raise ValidationError("Expected `%s`, got `%s`" % (
                    expected, data))
        if self.partial:
            dict_compare(ctx.render(self.partial), data)
        if self.partial_match:
            dict_compare(ctx.render(self.partial_match),
                         data, compare=match)
        if self.contains:
            for path in ctx.render(self.contains):
                mydata = data
                current = "."
                for k in path.split("."):
                    try:
                        mydata = mydata[k]
                    except KeyError:
                        raise ValidationError("Expected `%s` in `%s`" % (
                                              k, current))
                    current = ".".join([current, k])
