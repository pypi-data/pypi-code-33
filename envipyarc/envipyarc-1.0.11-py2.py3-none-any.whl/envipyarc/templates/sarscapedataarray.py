"""
Maps the SARSCAPEDATAARRAY data type to a DEFile datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate



class SARSCAPEDATAARRAY(ParamTemplate):
    """
    Defines the parameter template for the specified data type.
    """
    def get_parameter(self, task_param):
        # Input uses a composite data type of both defile and gpstring.
        # This allows for url strings while also providing file selection in the UI.
        if task_param['direction'].upper() == 'INPUT':
            return Template('''
        $name = arcpy.Parameter(
            displayName="$displayName",
            name="$name",
            datatype=["DEFile","GPString"],
            parameterType="$paramType",
            direction="$direction",
            multiValue=$multiValue
        )
''')
        # Return the output template
        else:
            return Template('''
        $name = arcpy.Parameter(
            displayName="$displayName",
            name="$name",
            datatype="GPString",
            parameterType="$paramType",
            direction="$direction",
            multiValue=$multiValue
        )
    ''')

    def parameter_names(self, task_param):
        return [Template('${name}')]

    def default_value(self):
        return Template('''
        ${name}.values = "$defaultValue"
''')

    def pre_execute(self):
        return Template('''
        paths = parameters[self.i${name}].valueAsText.split(';')
        paths = [ { 'url' : path } for path in paths ]
        input_params['${name}'] = paths
''')

    def post_execute(self):
        return Template('''
        if '${name}' in task_results:
            objs = task_results['${name}']
            paths = [ o['url'] for o in objs ]
            parameters[self.i${name}].values = paths
''')

def template():
    """Factory method for this parameter template class"""
    return SARSCAPEDATAARRAY('DEFile')
