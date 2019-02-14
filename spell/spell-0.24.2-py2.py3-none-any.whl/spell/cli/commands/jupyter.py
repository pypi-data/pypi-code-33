# -*- coding: utf-8 -*-
import atexit
import binascii
import json
import os
import shutil
import subprocess
import sys

import click

from spell.cli.commands.kill import kill
from spell.cli.commands.logs import logs
from spell.cli.commands.run import run
from spell.cli.commands.stop import stop
from spell.cli.exceptions import ExitException
from spell.cli.log import logger
from spell.cli.utils import cli_ssh_key_path
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    machine_config_params,
    cli_params,
    description_param,
)


@click.command(name="jupyter", short_help="Start a Spell Jupyter session")
@click.option("--system", is_flag=True,
              help="Install kernel to the system install directory")
@click.option("--lab", is_flag=True,
              help="Start up a JupyterLab session (defaults to Jupyter Notebook session)")
@machine_config_params
@dependency_params
@workspace_spec_params
@description_param
@cli_params
@click.pass_context
def jupyter(ctx, system, lab, machine_type, pip_packages, requirements_file, apt_packages,
            framework, python2, python3, conda_file, commit_ref,
            description, envvars, raw_resources, force, verbose, local_caching, provider, **kwargs):
    """
    Start a Spell Jupyter session

    The jupyter command creates a run on Spell infrastructure that supports running Jupyter cells remotely.
    Once the run reaches the "Running" state, locally installs a Jupyter kernel and spins up a Jupyter
    server in the current working directory.
    """
    try:
        from jupyter_client.kernelspec import KernelSpecManager
        from IPython.utils.tempdir import TemporaryDirectory
    except ImportError:
        raise ExitException("Failed to import Jupyter, see https://www.jupyter.org/install "
                            "for installation instructions.")

    if lab:
        try:
            from jupyterlab.labapp import main  # noqa
        except ImportError:
            raise ExitException("Failed to import JupyterLab, see "
                                "https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html "
                                "for installation instructions.")

    # Invoke the run command
    ctx.forward(run, run_type="jupyter", background=True)

    # Get necessary run metadata
    run_id = str(ctx.meta["run"].id)
    local_root = ctx.meta["local_root"]
    remote_root = ctx.meta["root_directory"]

    # Set up fallback terminate run
    def terminate_run():
        stopped = False
        logger.info("Stopping run {}".format(run_id))
        try:
            ctx.invoke(stop, run_ids=[int(run_id)], quiet=True)
            stopped = True
        except ExitException as e:
            logger.info("Exception while stopping run: {}".format(e))

        if stopped:
            return

        logger.info("Killing run {}".format(run_id))
        try:
            ctx.invoke(kill, run_ids=[int(run_id)], quiet=True)
        except ExitException as e:
            logger.info("Exception while killing run: {}".format(e))

    atexit.register(terminate_run)

    # Follow logs
    ctx.invoke(logs, run_id=run_id, follow=True, stop_status="running")

    # Build the argv
    cfg_handler = ctx.obj["config_handler"]
    argv = [
        sys.executable,
        "-m", "spell.cli.jupyter.spell_kernel",
        "--owner", cfg_handler.config.owner or cfg_handler.config.user_name,
        "--ssh-host", ctx.obj["ssh_args"]["ssh_host"],
        "--ssh-port", str(ctx.obj["ssh_args"]["ssh_port"]),
        "--api-url", ctx.obj["client_args"]["base_url"],
        "--api-version", ctx.obj["client_args"]["version_str"],
        "--api-token", cfg_handler.config.token,
        "--run-id", run_id,
    ]
    if local_root is not None and remote_root is not None:
        argv += [
            "--local-root", local_root,
            "--remote-root", remote_root,
        ]
    if conda_file is not None:
        argv += [
            "--conda-env", "spell",
        ]
    ssh_key_path = cli_ssh_key_path(cfg_handler)
    if os.path.isfile(ssh_key_path):
        argv += [
            "--key", ssh_key_path,
        ]
    if verbose:
        argv.append("--verbose")
    argv.append("{connection_file}")

    # Build the display name
    display_name = "Spell - "
    workspace = ctx.meta["run"].workspace
    # TODO(peter): Just check if the workspace is None after API omits them (CLI version >=0.12.0)
    if ctx.meta["run"].workspace is not None and workspace.id is not 0:
        workspace_name = ctx.meta["run"].workspace.name
        display_name += "{} on ".format(workspace_name)
    display_name += machine_type

    kernel_spec = {
        "argv": argv,
        "display_name": display_name,
    }

    # Install kernel
    name = "spell_" + hex(binascii.crc32(display_name.encode()))[2:10]
    with TemporaryDirectory() as tmpdir:
        os.chmod(tmpdir, 0o755)
        with open(os.path.join(tmpdir, "kernel.json"), "w") as kernel_file:
            json.dump(kernel_spec, kernel_file, sort_keys=True, indent=2)

        try:
            install_dir = KernelSpecManager().install_kernel_spec(tmpdir, name, user=(not system))
        except OSError as e:
            if system:
                raise ExitException("Permission denied. Installing to system requires running as root")
            else:
                raise e
    logger.info("Installed kernel {} ({})".format(name, display_name))

    # Set up uninstallation of kernel
    def uninstall():
        logger.info("Uninstalling kernel from {}".format(install_dir))
        shutil.rmtree(install_dir)

    atexit.register(uninstall)

    args = [
        "jupyter",
        "lab" if lab else "notebook",
        "--MappingKernelManager.default_kernel_name={}".format(name),
    ]
    jupyter_p = subprocess.Popen(args)
    while True:
        try:
            jupyter_p.wait()
            break
        except KeyboardInterrupt:
            pass
