from aether.proto import api_pb2
from aether.session.GlobalConfig import GlobalConfig
from aether.sky_utils import sky_utils


class SkyApplicationFrameworkServices(object):

    def SkyFrameworkComponent(self, builder, parameters, application_name, method, app=None):
        """Accesses a SkyApplicationFramework component registered on the platform.

        Args:
            builder (:py:class:`~base.SpacetimeBuilder.SpacetimeBuilder`): a SpacetimeBuilder or its Placeholder

            parameters (dict): a dictionary of parameters that can be json serialized.

            application_name (str): The name of the SkyApplicationFramework component registered on the platform.

            method (str): The name of the available method to call on the component.

        Returns:
            builder (:py:class:`~base.SpacetimeBuilder.SpacetimeBuilder`): the newly processed SpacetimeBuilder or its
             Placeholder
        """
        output_structure = api_pb2.SpacetimeBuilder()
        uri_parameters = dict(builder=sky_utils.serialize_pb(builder), method=method)
        uri_parameters.update(parameters)

        response = self._aether_client.post_to("SkyFrameworkComponent",
                                               dict(application_name=application_name),
                                               uri_parameters,
                                               output_structure=output_structure,
                                               app=app)
        return response
