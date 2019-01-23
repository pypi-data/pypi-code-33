import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserAdminServices(object):

    def UpgradeUserToDeveloper(self):
        """Runs a compiled applications from using its Application Id string.

        Returns:
            response (None): None if not successful; Status response is successful.
        """
        parameters = dict(method="UpgradeUserToDeveloper")
        response = self._aether_client.post_to("UserAdminInterface", {}, parameters)
        return response

    def GetUserInformation(self):
        """Retrieves user information, including profile and quota statistics.

        Returns:
            response (dict): dictionary of user information
        """
        parameters = dict(method="GetUserInformation")
        response = self._aether_client.post_to("UserAdminInterface", {}, parameters)
        return response

