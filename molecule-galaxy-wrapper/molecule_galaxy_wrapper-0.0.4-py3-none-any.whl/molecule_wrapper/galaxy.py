import subprocess


def install(requirements_path, roles_path, debug_mode=False):
    command = ["ansible-galaxy", "install", "--role-file",
               requirements_path, "--roles-path", roles_path, "--force"]

    if debug_mode:
        command.append("-vvv")

    subprocess.call(command)
