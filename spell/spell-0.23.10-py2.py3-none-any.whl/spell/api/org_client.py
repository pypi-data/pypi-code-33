from spell.api import base_client


ORG_RESOURCE_URL = "orgs"


class OrgClient(base_client.BaseClient):

    def create(self, name, billing_email):
        """Create a new org at the server

        Keyword arguments:
        name -- name of the new org (must be at least 4 characters)
        billing_email -- billing_email of the new org

        """
        payload = {
            "name": name,
            "billing_email": billing_email,
        }
        r = self.request("post", ORG_RESOURCE_URL, payload=payload)
        self.check_and_raise(r)
