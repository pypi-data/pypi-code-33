from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas._os import create_symlink
from compas._os import remove_symlink


__all__ = ['install_plugin']


def install_plugin(plugin):
    """Install a Python plugin for RhinoMac.

    Parameters
    ----------
    plugin : str
        The path to the plugin folder.
        For example, ``'path/to/RBE{520ddb34-e56d-4a37-9c58-1da10edd1d62}'``.

    Examples
    --------
    .. code-block:: bash

        >>> import compas_rhino
        >>> compas_rhinomac.install_plugin('path/to/RBE{520ddb34-e56d-4a37-9c58-1da10edd1d62}')

    .. code-block:: bash

        $ python -m compas_rhinomac.install_plugin path/to/RBE{520ddb34-e56d-4a37-9c58-1da10edd1d62}

    """
    mac = 'Library/Application Support/McNeel/Rhinoceros/MacPlugIns/PythonPlugIns'

    source_parent_dir, plugin_name = os.path.split(plugin)
    if not source_parent_dir:
        source_parent_dir = os.getcwd()
    source = os.path.join(source_parent_dir, plugin_name)

    if not os.path.isdir(source):
        raise Exception('Cannot find the plugin: {}'.format(source))

    if not os.path.isdir(os.path.join(source, 'dev')):
        raise Exception('The plugin does not contain a dev folder.')

    if not os.path.isfile(os.path.join(source, 'dev', '__plugin__.py')):
        raise Exception('The plugin does not contain plugin info.')

    destination_parent_dir = os.path.join(os.environ['HOME'], mac)
    destination = os.path.join(destination_parent_dir, plugin_name)

    print('Installing PlugIn {} to RhinoMac PythonPlugIns.'.format(plugin_name))

    if os.path.exists(destination):
        remove_symlink(destination)
    create_symlink(source, destination)

    print('PlugIn {} Installed.'.format(plugin_name))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('plugin_path', help="The path to the plugin.")

    args = parser.parse_args()

    install_plugin(args.plugin_path)
