from py_buildsystem.Step.StepCompile import StepCompile
from py_buildsystem.Step.StepLink import StepLink


class StepFactory:
    @staticmethod
    def create(step_config, object_to_inject=None):
        step_identifier = list(step_config.keys())[0].split(" ")

        step_type = step_identifier[0]
        step_name = " ".join(step_identifier[1:])

        if 'compile' in step_type:
            return StepCompile(step_config, step_name, object_to_inject.get_compiler())
        elif 'link' in step_type:
            return StepLink(step_config, step_name, object_to_inject.get_linker())
        else:
            raise TypeError('Unsuported step type')
