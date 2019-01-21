import sys
import urllib

from aiohttp.client_exceptions import ContentTypeError

from santa.task import Task
from santa.extractor import extractor_factory
from santa.validator import validator_factory, ValidationError
from santa.shell import TestShell

from santa.parser import (YamlLoader, MappingField, StringField,
                          ListField, BooleanField,
                          LazyObjField)
from santa.builtins.validators import StatusValidator


class ExtractListField(ListField):
    def __init__(self, **kwargs):
        super().__init__(item_type=extractor_factory, **kwargs)


class ValidateListField(ListField):
    def __init__(self, **kwargs):
        super().__init__(item_type=validator_factory, **kwargs)


class URL(YamlLoader):
    __yaml_name__ = "url"
    scheme = StringField()
    host = StringField()
    path = StringField(default="/")
    port = StringField(default="")
    headers = MappingField(default=dict)
    query_string = MappingField(default=dict)

    def build(self, ctx):
        port = ":%s" % self.port if self.port else ""
        netloc = self.host + port
        pr = urllib.parse.ParseResult(self.scheme, netloc, self.path,
                                      [], [], [])
        return (ctx.render(pr.geturl()), self.build_qs(ctx),
                ctx.render(self.headers))

    def build_qs(self, ctx):
        # TODO: handle lists
        return [(k, ctx.render(v))
                for k, v in ctx.render(self.query_string).items()]


EXPECTED_STATUS = {
    "GET": [200],
    "POST": [200, 201, 204],
    "PATCH": [200, 201, 204],
    "PUT": [200, 201, 204],
    "DELETE": [200, 202, 204],
}


class Test(Task):
    """
    Test an HTTP request. Validators and extractors can be provided.
    """
    method = StringField(choice=["GET", "POST", "PUT", "DELETE",
                                 "OPTION", "HEAD"],
                         default="GET",
                         help="HTTP method of the request")
    url = LazyObjField(URL, help="URL object to test")
    json_body = MappingField(default=None, help="JSON data sent")
    validate = ValidateListField(default=list, help="List of validators")
    extract = ExtractListField(default=list, help="List of extractors")
    debug = BooleanField(default=False, help="Outut debug logs")
    interactive = BooleanField(default=False)
    pdb = BooleanField(default=False)

    def get_parts(self, ctx):
        url, qs, headers = self.url.build(ctx)
        json_body = ctx.render(self.json_body)
        return url, qs, headers, json_body

    async def __run__(self, ctx):
        self.__ctx__ = ctx
        if self.pdb:
            import ipdb;
            ipdb.set_trace()
        url, qs, headers, json_body = self.get_parts(ctx)

        if self.interactive:
            cli = TestShell(self, ctx)
            await cli.cmdloop()
            self._result = cli.task._result
            return

        self._result.log_debug("request:")
        self._result.log_debug((url, qs, headers), 1)
        self._result.log_debug(json_body, 1)

        self._result["request"] = dict(
            method=self.method,
            url=url,
            query_string=qs,
            headers=headers,
            json=json_body
        )
        sess = ctx["_http_session"]
        executor = getattr(sess, self.method.lower())
        async with executor(url, params=qs,
                            headers=headers, json=json_body) as resp:
            self._result.log_debug("response:")
            self._result.log_debug(resp.status, 1)
            self._result.log_debug(await resp.text(), 1)
            self._result.log_debug("")
            self._result["response.status"] = resp.status
            try:
                self._result["response.json"] = await resp.json()
            except ContentTypeError:
                self._result["response.json"] = None
                pass
            if self._result["response.json"] is None:
                self._result["response.text"] = await resp.text()
            else:
                self._result["response.text"] = None
            await self.validate_response(ctx, resp)
            await self.extract_values(ctx, resp)

    async def validate_response(self, ctx, response):
        got_status = False
        for v in self.validate:
            if v.__yaml_name__ == "status":
                got_status = True
            try:
                await v(response, ctx)
            except ValidationError as e:
                self._result.log_error(str(e))
        if not got_status:
            v = StatusValidator(
                    expected=EXPECTED_STATUS.get(self.method.upper(), [200]))
            try:
                await v(response, ctx)
            except ValidationError as e:
                self._result.log_error(str(e))

    async def extract_values(self, ctx, response):
        try:
            for e in self.extract:
                await e(response, ctx)
        except Exception as ex:
            self._result.log_exception(ex, sys.exc_info()[2])
