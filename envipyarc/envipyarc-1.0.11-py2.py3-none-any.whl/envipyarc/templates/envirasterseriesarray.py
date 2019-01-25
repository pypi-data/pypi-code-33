"""
Maps the ENVIRASTERSERIESARRAY data type to a GPTool datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate


class ENVIRASTERSERIESARRAY(ParamTemplate):
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
        ${name}.values = "$defaultValue"
''')

    def update_parameter(self):
        return Template('')

    def pre_execute(self):
        return Template('''

        paths = parameters[self.i${name}].values
        series = []
        for path in paths:
            series.append({'url': path.value, 'factory':'ENVIURLRASTERSERIES'})
        input_params['${name}'] = series
''')

    def post_execute(self):
        return Template('''
        if '${name}' in task_results:
            series = task_results['${name}']
            paths = []
            for s in series:
                path = s['url']
                if path not in paths:
                    paths.append(path)
            parameters[self.i${name}].values = paths
''')


def template():
    """Returns the template object."""
    return ENVIRASTERSERIESARRAY('DEFile')
