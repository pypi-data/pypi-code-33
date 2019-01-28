import json

class sky_app_utils(object):

    @staticmethod
    def verify_sky_app(sky_app):
        """
        SkyApplications can contain a linear sequence of SkyMessages that will be run as an application.
        Future iterations will allow SkyApplications to contain Applications, thus supporting arbitrary
        tree sequences of applications. Currently, SkyApplications are not supported.

        The inner and outer structure of the application is defined in its description. As a result, the
        input and output of each SkyMessage must match the inner and outer structure of the SkyApplication, and
        must match each input-output pass through of the SkyMessages

        Currently, all SkyApplication inputs must be one PlaceholderPolygon.

        For example, a simple Search -> Crop -> Download application.

        input_structure = dict(polygon=PlaceholderPolygon)  <-- This is the only currently supported case.
        output_structure = dict(my_file=Spacetime)  <--- the key can be any string, the value is the return of Download.

        The application itself consists of SkyMessages.
        The Search SkyMessage will contain:

        input_structure = dict(polygon=PlaceholderPolygon)
        output_structure = dict(generated_id=SpacetimeBuilder)
        request = "...search.bytestring..." expecting polygon replacement.

        and so on.

        :return: True or False, whether the SkyApplication passes its verification checks.
        """

        if len(sky_app.applications) != 0:
            return False

        if len(sky_app.messages) == 0:
            return False

        if sky_app.input_structure != json.dumps(dict(polygon="PlaceholderPolygon")):
            return False

        return True