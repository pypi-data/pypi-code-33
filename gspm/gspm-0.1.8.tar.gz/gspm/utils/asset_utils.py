
import logging
import gspm.utils.git_utils as git_utils
import gspm.utils.path_utils as path_utils
from distutils.dir_util import copy_tree
import os
import urllib


#   copy asset from repo to project
def copy_asset(project, asset):

    logging.debug("[asset_utils] copy")

    for include in asset.includes:

        from_dir = os.path.abspath("{0}/{1}/{2}".format(project.repository_path, asset.name, include.dir))
        to_dir = os.path.abspath("{0}/{1}".format(project.project_path, include.todir))

        if not os.path.exists(from_dir):
            raise Exception("Could not Locate Path [{0}]".format(from_dir))

        if not os.path.exists(to_dir):
            logging.debug("- creating folder [{0}]".format(to_dir))
            os.mkdir(to_dir)

        logging.debug("- copying asset from [{0}] to [{1}]".format(from_dir, to_dir))

        try:
            copy_tree(from_dir, to_dir)
            # ret = copy_tree(from_dir, to_dir, dry_run=1, )
            # print(ret)
        except Exception as e:
            raise Exception(e)


#   pull asset from location
def pull_asset(project, asset):
    logging.debug("[asset_utils] pull")
    if asset.type == "git":
        _pull_asset_git(project, asset)
        return
    if asset.type == "local":
        _pull_asset_local(project, asset)
        return
    if asset.type == "local_copy":
        _pull_asset_local(project, asset)
        return
    if asset.type == "local_zip":
        _pull_asset_local(project, asset)
        return
    raise Exception("Unknown Asset Type [{0}]".format(asset.type))


#   clean asset
def clean_asset(project, asset):
    logging.debug("[asset_utils] clean")
    #   remove from repository
    path_utils.clean_path(path_utils.create_repo_path(project, asset))
    #   remove from project
    for include in asset.includes:
        to_dir = "{0}/{1}".format(project.project_path, include.todir)
        path_utils.clean_path(to_dir)


#   get destination path
def _get_dest_path(project, asset):
    logging.debug("[asset_utils] _get_dest_path")
    return "{0}/{1}".format(project.repository_path, asset.name)


#   pull asset using git
def _pull_asset_git(project, asset):

    logging.debug("[asset_utils] _pull_asset_git")

    try:

        if 'branch' not in asset:
            asset.branch = 'master'

        git_utils.pull(asset.location, asset.branch, _get_dest_path(project, asset))

    except Exception as e:

        logging.error(e)
        raise Exception("Error Occured using GIT")


#   pull asset from local filesystem
def _pull_asset_local(project, asset):

    logging.debug("[asset_utils] _pull_asset_local")

    logging.debug(urllib.request.url2pathname(asset.location))
    logging.debug(os.path.abspath(urllib.request.url2pathname(asset.location)))

    from_dir = "{0}".format(os.path.abspath(os.path.abspath(urllib.request.url2pathname(asset.location))))
    to_dir = "{0}/{1}".format(project.repository_path, asset.name)

    logging.debug("- grabbing local copy of asset from [{0}] to [{1}]".format(from_dir, to_dir))

    try:
        copy_tree(from_dir, to_dir)
    except Exception as e:
        raise Exception(e)

        
