
import logging
import os
import shutil
import stat
import zipfile


#   define the paths for the project
def define_project_paths(project):
    #   define home path
    project.home_path = os.path.abspath('.')

    #   define project path
    project.project_path = os.path.abspath('{0}'.format(project.config.path))

    #   define repo home
    project.repository_home = os.path.abspath('{0}/.repo/'.format(project.home_path))

    #   define project repository path
    project.repository_path = os.path.abspath('{0}/.repo/{1}'.format(project.home_path, project.config.name))


def copy_path(project, path, dest_path):

    if not os.path.exists(path):
        raise Exception("Could Not Find Path [{0}] to Copy".format(path))

    if os.path.exists(dest_path):
        if not project.config.force:
            raise Exception("Destination Path [{0}] Already Exists, try using the --force".format(dest_path))


def clean_path(path):
    logging.debug("[path_utils] clean_path")
    _path = os.path.abspath(path)
    logging.info(_path)
    if os.path.exists(_path):
        shutil.rmtree(_path, ignore_errors=False, onerror=__remove_read_only)


def create_path(path):
    logging.debug("[path_utils] create_path")
    _path = os.path.abspath(path)
    logging.info(_path)
    if not os.path.exists(_path):
        os.makedirs(_path)


def create_repo_path(project, asset):
    return "{0}/{1}".format(project.repository_path, asset.name)


def __remove_read_only(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


