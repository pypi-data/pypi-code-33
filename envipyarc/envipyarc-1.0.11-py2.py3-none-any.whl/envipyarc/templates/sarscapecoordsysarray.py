"""
Maps the SARSCAPECOORDSYSARRAY data type to a GPTool datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate


class SARSCAPECOORDSYSARRAY(ParamTemplate):
    """
    Class template for the datatype
    """
    def get_parameter(self, task_param):
        if task_param['direction'].upper() == 'OUTPUT':
            return Template('''
        $name = arcpy.Parameter(
            displayName="$displayName",
            name="$name",
            datatype="$dataType",
            parameterType="$paramType",
            direction="$direction",
            multiValue=False
        )
''')
        # Return the input template
        return Template('''
        $name = arcpy.Parameter(
            displayName="$displayName",
            name="$name",
            datatype=["$dataType","GPString"],
            parameterType="$paramType",
            direction="$direction",
            multiValue=False
        )
''')

    def parameter_names(self, task_param):
        return [Template('$name')]

    def default_value(self):
        # normally, default is: "['GEO-GLOBAL', '', 'GEO', '', 'WGS84', '']"
        return Template('''
        ${name}.value = 4326
''')

    def update_parameter(self):
        return Template('')

    def pre_execute(self):
        # sarscapecoordsys itself is a StrArr of length 7
        return Template('''

        strArr = [""] * 7
        css = parameters[self.i${name}].valueAsText
        strArr[0] = css.replace("'", '"') 
        input_params['${name}'] = strArr
''')

    def post_execute(self):
        return Template('''
        if '${name}' in task_results:
            pass
''')


def template():
    """Returns the template object."""
    return SARSCAPECOORDSYSARRAY('GPCoordinateSystem')
