from deprecated import deprecated
from .process import FGProcess

_PROCESS = None


def get_process():
    if _PROCESS is None:
        raise NameError(
            f"call set_paths(app_dir, data_root) before accessing the global process."
        )
    else:
        return _PROCESS


@deprecated(reason="Use FGProcess instead")
def set_paths(app_dir, data_root):
    global _PROCESS
    _PROCESS = FGProcess(app_dir, data_root)
    _PROCESS.data.paths["app"] = app_dir


@deprecated(reason="Use FGProcess.parameters instead")
def get_parameter(key):
    return get_process().parameters[key]


@deprecated(reason="Use FGProcess.input instead")
def get_input_path(filename):
    return get_process().input[filename].path


@deprecated(reason="Use FGProcess.output instead")
def get_output_path(filename):
    return get_process().output[filename].path


@deprecated(reason="Use FGProcess.summary or FGProcess.output['summary'] instead")
def get_summary_path():
    return get_process().output["summary"].path


@deprecated(reason="Use FGProcess.data.paths instead")
def get_paths():
    return {**get_process().data.paths, "app": get_process().app.app_dir}


@deprecated(reason="Use FGProcess.app.manifest instead")
def get_app_manifest():
    return get_process().app.manifest


@deprecated(reason="Use FGProcess.parameters instead")
def get_parameters():
    return {
        name: param.value for name, param in get_process().parameters.parameter.items()
    }
