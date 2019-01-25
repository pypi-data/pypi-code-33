"""
Maps the ENVI Task data type to a GPTool datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate


class ENVIRASTERARRAY(ParamTemplate):
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
        rasters = []
        for path in paths:
            rasters.append({'url': path.value, 'factory':'URLRaster'})
        input_params['${name}'] = rasters
''')

    def post_execute(self):
        return Template('''

        if '${name}' in task_results:
            rasters = task_results['${name}']
            paths = []
            for raster in rasters:
                if 'url' in raster:
                    path = raster['url']
                    if path not in paths:
                        paths.append(path)
                else:
                    # some raster types are not supported, such as ENVISubsetRaster
                    import json
                    messages.addErrorMessage("This task may not be supported: one or more returned ENVIRaster(s) are of an unexpected dehydrated form: " + json.dumps(raster))
                    raise arcpy.ExecuteError
            parameters[self.i${name}].values = paths
''')


def template():
    """Returns the template object."""
    return ENVIRASTERARRAY('DERasterDataset')
