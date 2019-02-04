from spell.api import base_client


TEMPLATE_RESOURCE_URL = "dockertemplate"


class TemplateClient(base_client.BaseClient):
    def __init__(self, resource_url=TEMPLATE_RESOURCE_URL, **kwargs):
        self.resource_url = resource_url
        super(TemplateClient, self).__init__(**kwargs)

    def get_template(self):
        """Get dockerfile template

        Returns:
        the template string retrieved from the server
        """
        r = self.request("get", self.resource_url)
        self.check_and_raise(r)
        template = self.get_json(r)["template"]
        return template.body
