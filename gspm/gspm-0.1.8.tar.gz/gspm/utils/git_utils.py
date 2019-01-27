
import git
import logging


def pull(url, branch, dest):
    try:
        logging.debug("[git_utils] pull")
        logging.debug("- using git to pull branch {0} from {1}".format(branch, url))
        git.Repo.clone_from(url, dest, branch=branch)
    except Exception as e:
        raise Exception(e)




