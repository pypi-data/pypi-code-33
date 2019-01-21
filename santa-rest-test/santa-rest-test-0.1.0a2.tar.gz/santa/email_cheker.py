import time

from restinpy.parser import StringField, IntField
from restinpy.task import Task


class EmailChecker(Task):
    from_ = StringField(help="Sender email address", default="")
    to = StringField(help="Recipent email address", default="")
    created_since = IntField(help="Seconds interval since email creation.",
                             default=10)
    timeout = IntField("Retry duration before fail", default=30)

    async def __call__(self, ctx):
        raise NotImplementedError("Define an email checker backend")


class MailhogEmailChecker(EmailChecker):
    async def __call__(self, ctx):
        session = ctx["_http_session"]
        url = "%s/api/v2/messages?limit=100" % ctx["mailhog"]["base_url"]
        start = time.time()
        while time.time() - start < self.timeout:
            async with session.get(url, params=(("limit", 100),)) as resp:
                resp = await resp.json()
                await self.validate_response(ctx, resp)
                await self.extract_values(ctx, resp)
