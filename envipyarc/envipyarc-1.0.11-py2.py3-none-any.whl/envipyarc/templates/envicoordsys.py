"""
Maps the ENVICOORDSYS data type to a GPTool datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate


class ENVICOORDSYS(ParamTemplate):
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
            multiValue=$multiValue
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
            multiValue=$multiValue
        )
''')

    def parameter_names(self, task_param):
        return [Template('$name')]

    def default_value(self):
        return Template('''
        ${name}.value = "$defaultValue"
''')

    def update_parameter(self):
        return Template('')

    def pre_execute(self):
        return Template('''

        coordSysStr = parameters[self.i${name}].valueAsText
        # ENVICoordSys parses based on " delimiters, not '
        coordSysStr = coordSysStr.replace("'", '"') 
        input_params['${name}'] = {'coord_sys_str': coordSysStr, 'factory':'CoordSys'}
''')

    def post_execute(self):
        return Template('''
        if '${name}' in task_results:
            coordSys = task_results['${name}']
            key = 'coord_sys_str'
            if key not in coordSys:
                key = 'coord_sys_code'
            parameters[self.i${name}].values = coordSys[key]
''')


def template():
    """Returns the template object."""
    return ENVICOORDSYS('GPCoordinateSystem')
