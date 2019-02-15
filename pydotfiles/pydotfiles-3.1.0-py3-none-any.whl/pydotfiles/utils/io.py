# General imports
import os
import os.path
import shutil
import subprocess

# Project imports
from .general import hash_file


"""
I/O-related public access helper methods
"""


def mv_file(origin, destination, use_sudo=False, sudo_password=""):
    # Fast fail if invalid origin/destinations passed in
    if origin is None or destination is None:
        raise RuntimeError(f"File Moving: Invalid file paths passed in [origin={origin}, destination={destination}]")

    # Fast return if there is no need for the operation
    if is_moved(origin, destination):
        return

    # Fail fast if a destination file already exists
    if os.path.isfile(destination) or os.path.islink(destination):
        raise RuntimeError(f"File Moving: Destination file already exists [origin={origin}, destination={destination}]")

    if use_sudo:
        command = f"mv {origin} {destination}"
        process = subprocess.Popen(['sudo', '-S'] + command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        try:
            stdout, stderr = process.communicate(sudo_password + '\n', timeout=3)

            if "File exists" in stderr:
                raise FileExistsError(f"The file {destination} already exists")

            if process.returncode != 0:
                raise RuntimeError(stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            raise
    else:
        shutil.move(origin, destination)


def rm_file(file, use_sudo=False, sudo_password=""):
    # Fast fail if invalid file is passed in
    if file is None:
        raise RuntimeError(f"File Removing: Invalid file passed in [file={file}]")

    # Fast return if there is no need for the operation
    if not os.path.isfile(file) and not is_broken_link(file):
        return

    if use_sudo:
        command = f"rm {file}"
        process = subprocess.Popen(['sudo', '-S'] + command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        try:
            stdout, stderr = process.communicate(sudo_password + '\n', timeout=3)

            if process.returncode != 0:
                raise RuntimeError(stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            raise
    else:
        os.unlink(file)


def copy_file(origin, destination, use_sudo=False, sudo_password=""):
    # Fast fail if invalid origin/destinations passed in
    if origin is None or destination is None:
        raise RuntimeError(f"File Copying: Invalid symlinking file paths passed in [origin={origin}, destination={destination}]")

    # Fast return if there is no need for the operation
    if is_copied(origin, destination):
        return

    # Fast fail if the file already exists
    if os.path.isfile(destination) or os.path.islink(destination):
        raise RuntimeError(f"File Copying: Destination file already exists [origin={origin}, destination={destination}]")

    if use_sudo:
        command = f"cp {origin} {destination}"
        process = subprocess.Popen(['sudo', '-S'] + command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        try:
            stdout, stderr = process.communicate(sudo_password + '\n', timeout=3)

            if "File exists" in stderr:
                raise FileExistsError(f"The file {destination} already exists")

            if process.returncode != 0:
                raise RuntimeError(stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            raise
    else:
        shutil.copy2(origin, destination)


def symlink_file(origin, destination, use_sudo=False, sudo_password=""):
    # Fast fail if invalid origin/destinations passed in
    if origin is None or destination is None:
        raise RuntimeError(f"File Symlinking: Invalid symlinking file paths passed in [origin={origin}, destination={destination}]")

    # Fast return if there is no need for the operation
    if is_linked(origin, destination):
        return

    # Fast fail if the file already exists
    if os.path.isfile(destination) or os.path.islink(destination):
        raise RuntimeError(f"File Symlinking: Destination file already exists [origin={origin}, destination={destination}]")

    if use_sudo:
        command = f"ln -s {origin} {destination}"
        process = subprocess.Popen(['sudo', '-S'] + command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        try:
            stdout, stderr = process.communicate(sudo_password + '\n', timeout=3)

            if "File exists" in stderr:
                raise FileExistsError(f"The file {destination} already exists")

            if process.returncode != 0:
                raise RuntimeError(stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            raise
    else:
        os.symlink(origin, destination)


def unsymlink_file(file, use_sudo=False, sudo_password=""):
    # Fast fail if invalid file name or type passed in
    if file is None or not os.path.islink(file):
        raise RuntimeError(f"File Unsymlinking: File does not exist or is a symlink [file={file}]")

    if use_sudo:
        command = f"unlink {file}"
        process = subprocess.Popen(['sudo', '-S'] + command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        try:
            stdout, stderr = process.communicate(sudo_password + '\n', timeout=3)

            if "File exists" in stderr:
                raise FileExistsError(f"The file {file} already exists")

            if process.returncode != 0:
                raise RuntimeError(stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            raise
    else:
        os.unlink(file)


def run_file(file, use_sudo=False, sudo_password=""):
    # Fast fail if there is no file or the file can't be executed
    if file is None or not is_executable(file):
        raise RuntimeError(f"File Execution: File does not exist or have execution permissions [file={file}]")

    if use_sudo:
        command = f"{file}"
        process = subprocess.Popen(['sudo', '-S'] + command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        try:
            stdout, stderr = process.communicate(sudo_password + '\n', timeout=3)

            if process.returncode != 0:
                raise RuntimeError(stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            raise
    else:
        command_result = subprocess.run(file)

        if command_result.returncode != 0:
            raise RuntimeError(command_result.stderr.decode())


def run_command(command, use_sudo=False, sudo_password="", check_output=True):
    # Fast fail if invalid command is passed in
    if command is None:
        raise RuntimeError(f"Command Execution: Invalid command passed in [command={command}]")

    if use_sudo:
        run_command_with_communication(f"sudo -S {command}", sudo_password, check_output)
    else:
        output = subprocess.run(command, encoding='utf-8', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if check_output and output.returncode != 0:
            raise RuntimeError(f"Command Execution: A given command had a non-zero return code [command='{command}', err='{output.stderr}']")

        return output.stdout.strip()


def run_command_with_communication(command, communication, check_output=True):
    process = subprocess.Popen(command.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

    try:
        stdout, stderr = process.communicate(communication + '\n')

        if check_output and process.returncode != 0:
            raise RuntimeError(f"Command Execution: A given command had a non-zero return code [command='{command}', err='{stderr}']")

        return stdout.strip()
    except subprocess.TimeoutExpired:
        process.kill()
        raise


"""
Utility functions
"""


def is_moved(origin, destination):
    # Enables fast-failing based on existence
    if not os.path.isfile(destination):
        return False

    if os.path.isfile(origin):
        return False

    return True


def is_broken_link(file):
    return os.path.islink(file) and not os.path.exists(file)


def is_linked(origin, destination):
    return os.path.islink(destination) and os.path.realpath(destination) == os.path.realpath(origin)


def is_copied(origin, destination):
    # Enables fast-failing based on type
    if os.path.islink(destination):
        return False

    # Enables fast-failing based on existence
    if not os.path.isfile(destination):
        return False

    # Enables fast-failing based on file size
    origin_file_size = os.stat(origin).st_size
    destination_file_size = os.stat(destination).st_size

    if origin_file_size != destination_file_size:
        return False

    # Enables fast-failing based on metadata
    origin_last_modified_time = os.path.getmtime(origin)
    destination_last_modified_time = os.path.getmtime(destination)

    if origin_last_modified_time != destination_last_modified_time:
        return False

    # Loads in the files and checks that their hashes are the same
    origin_file_hash = hash_file(origin)
    destination_file_hash = hash_file(destination)
    return origin_file_hash == destination_file_hash


def is_executable(file):
    return os.access(file, os.X_OK)
