"""
Maps the ENVI Task data type to a GPTool datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate


class ENVIRASTER(ParamTemplate):
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

        path = parameters[self.i${name}].valueAsText
        input_params['${name}'] = {'url': path, 'factory':'URLRaster' }
''')

    def post_execute(self):
        return Template('''
        if '${name}' in task_results:
            raster = task_results['${name}']
            if 'url' in raster:
                parameters[self.i${name}].value = raster['url']
            else:
                # some raster types are not supported, such as ENVISubsetRaster
                import json
                messages.addErrorMessage("This task may not be supported: the returned ENVIRaster is of an unexpected dehydrated form: " + json.dumps(raster))
                raise arcpy.ExecuteError
''')


def template():
    """Returns the template object."""
    return ENVIRASTER('DERasterDataset')
