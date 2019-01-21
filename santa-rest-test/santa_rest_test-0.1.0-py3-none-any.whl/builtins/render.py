from base64 import b64encode
from urllib.parse import urlunparse, urlencode

from santa.context import RenderFunction


class BasiAuth(RenderFunction):
    func_name = "basic_auth"

    def __call__(self, username, password):
        concat = "%s:%s" % (username, password)
        b64 = b"Basic %s" % b64encode(concat.encode())
        return b64.decode()


class RenderUrl(RenderFunction):
    func_name = "render_url"

    def __call__(self, urldef):
        urldef = self.ctx.render(urldef)
        port = ":%s" % urldef["port"] if "port" in urldef else ""
        netloc = urldef["host"] + port
        # TODO: handle lists
        qs = self.ctx.render(urldef.get("query_string", {}))
        return urlunparse((urldef["scheme"], netloc, urldef["path"],
                           [], urlencode(qs), []))
