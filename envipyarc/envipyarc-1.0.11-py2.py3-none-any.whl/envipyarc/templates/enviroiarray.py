"""
Maps the ENVIROIARRAY data type to a GPTool datatype
"""
from __future__ import absolute_import
from string import Template

from envipyarclib.gptool.parameter.template import Template as ParamTemplate


class ENVIROIARRAY(ParamTemplate):
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
        # one file input, containing multiple rois
        return Template('''

        paths = parameters[self.i${name}].values
        rois = []
        for path in paths:
            rois.append({'url': path.value, 'factory':'ENVIURLROI'})
        input_params['${name}'] = rois
''')

    def post_execute(self):
        # return multiple rois, but each exist in the same file
        return Template('''
        if '${name}' in task_results:
            rois = task_results['${name}']
            paths = []
            for roi in rois:
                path = roi['url']
                if path not in paths:
                    paths.append(path)
            parameters[self.i${name}].values = paths
''')


def template():
    """Returns the template object."""
    return ENVIROIARRAY('DEFile')
