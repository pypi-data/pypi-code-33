import json
import os
import shutil

from orchestrate.common import safe_format, TemporaryDirectory
from orchestrate.core.services.base import Service
from orchestrate.core.lib.types import *
from orchestrate.version import DOCKER_IMAGE_VERSION

LANGUAGE_MAP = {
  'python3.6': 'python3.6',
  'python3': 'python3.6',
  'python2.7': 'python2.7',
  'python2': 'python2.7',
  'python': 'python2.7',
}
PYTHON_VERSION_MAP = {
  'python3.6': '3.6',
  'python2.7': '2.7',
}
FRAMEWORK_MAP = {
  'python': 'python',
  'cuda': 'cuda-9.0',
  'tensorflow': 'tensorflow-gpu',
  'theano': 'theano-gpu',
  'keras': 'keras-gpu',
  'pytorch': 'pytorch-gpu',
  'mxnet': 'mxnet-gpu',
}
SUPPORTED_LANGUAGES = sorted(set(LANGUAGE_MAP.values()))

def sanitize_command(cmd):
  return '' if cmd is None else str(cmd)

def sanitize_command_str_or_list(cmds):
  if cmds:
    return [sanitize_command(cmd) for cmd in cmds] if is_sequence(cmds) else [sanitize_command(cmds)]
  else:
    return []

class ModelPackerService(Service):
  def build_image(
    self,
    image_name,
    directory,
    install_commands,
    run_commands,
    optimization_options,
    language,
    framework,
    pythonpath,
    quiet=False,
  ):
    actual_language = LANGUAGE_MAP.get(language or 'python')
    actual_framework = framework or 'python'
    if actual_language is None:
      raise Exception(safe_format(
        "The language {} is not currently supported by orchestrate. Supported languages are {}.",
        language,
        ", ".join(SUPPORTED_LANGUAGES),
      ))
    python_version = PYTHON_VERSION_MAP[actual_language]
    base_image = safe_format(
      'orchestrate/{}-{}:{}',
      FRAMEWORK_MAP[actual_framework],
      python_version,
      DOCKER_IMAGE_VERSION,
    )

    with TemporaryDirectory() as root_dirname:
      source_directory = directory
      destination_directory = os.path.join(root_dirname, 'orchestrate')
      bin_dirname = os.path.join(root_dirname, 'bin')
      etc_dirname = os.path.join(root_dirname, 'etc', 'orchestrate')
      var_dirname = os.path.join(root_dirname, 'var', 'orchestrate')
      shutil.copytree(source_directory, destination_directory)
      for dirname in (bin_dirname, etc_dirname, var_dirname):
        os.makedirs(dirname)

      config = {
        'metrics': optimization_options['metrics'],
        'parameters': optimization_options.get('parameters', []),
        'run_commands': sanitize_command_str_or_list(run_commands),
      }
      with open(os.path.join(etc_dirname, 'config.json'), 'w') as config_fp:
        json.dump(config, config_fp)

      return self.services.docker_service.build(
        tag=image_name,
        directory=root_dirname,
        dockerfile_contents=self.services.template_service.render_template_from_file(
          'model_packer/Dockerfile.ms',
          dict(
            base_image=base_image,
            install_commands=sanitize_command_str_or_list(install_commands),
            pythonpath=pythonpath,
          ),
        ),
        quiet=quiet,
        show_all_logs=True,
      )
