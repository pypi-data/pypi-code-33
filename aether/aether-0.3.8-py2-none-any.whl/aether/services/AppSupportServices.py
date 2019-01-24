from aether.proto import api_pb2
from aether.session.GlobalConfig import GlobalConfig
from aether.sky_utils import sky_utils


class AppSupportServices(object):

    def ApplicationPayload(self, application_name="", description=""):
        """Compiles a series of operations into a single encoded payload string.

        Args:
            application_name (str): The desired name of the application.

            description (str): A string description of the application, visible to those who use the application.

        Returns:
            payload (str): A serialized encoding of the application process.
        """

        sky_app = api_pb2.SkyApplication()
        sky_app.application_name = application_name
        sky_app.description = description
        sky_app.owner_uuid = GlobalConfig._getInstance().uuid

        app = self._app
        if app is None or len(app._messages) == 0:
            return sky_app

        sky_app.messages.extend(app._messages)
        # sky_app.input_structure = app._messages[0].input_structure
        sky_app.output_structure = app._messages[-1].output_structure
        return sky_utils.serialize_for_url(sky_utils.serialize_pb(sky_app))

    def PublishApplication(self, payload):
        """Publishes a payload to the Aether platform to be accessed by application Id via URL or the Aether Network.

        Args:
            payload (str): The serialized encoding of the application produced by :py:class:`~Sky.Sky` ApplicationPayload method.

        Returns:
            application_id (str): A unique id to access the application via URL or the Aether Network.
        """

        uri_parameters = dict(payload=payload, method="PublishApp")
        response = self._aether_client.post_to("AppSupportInterface", {}, uri_parameters)
        return response

    def UpdateApplication(self, application_id, payload):
        """Updates a payload to the Aether platform previously created by :py:class:`~Sky.Sky` PublishApplication method.

        Args:
            application_id (str): The unique id of the application.

            payload (str): The serialized encoding of the application produced by :py:class:`~Sky.Sky` ApplicationPayload method.

        Returns:
            application_id (str): The same application_id.
        """

        uri_parameters = dict(payload=payload, method="UpdateApp", application_id=application_id)
        response = self._aether_client.post_to("AppSupportInterface", {}, uri_parameters)
        return response

    def GetUserApps(self):
        """
        The GetUserApps retrieves all the published Apps for the user, and the Apps' information.

        Returns:
            a JSON dictionary containing application_id-info_dict pairs for all user applications.
        """
        uri_parameters = dict(method="GetUserApps")
        response = self._aether_client.post_to("AppSupportInterface", {}, uri_parameters)
        return response

    def GetAppInfo(self, application_id):
        """
       The GetAppInfo retrieves all the information on the the published application_id.

       Returns:
            a JSON dictionary containing the application information
       """

        uri_parameters = dict(method="GetAppInfo", application_id=application_id)
        response = self._aether_client.post_to("AppSupportInterface", {}, uri_parameters)
        return response
