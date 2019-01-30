import os
import subprocess
import sys

from onepanel.utilities.connection import Connection
from onepanel.commands.projects import ProjectViewController

# The maximum file-size for a file to be committed:
max_file_size = 50 * 1024  # in KiB (= 1024 byte), 50 MB
max_repo_size = 500 * 1024  # in KiB, 200 MB
units = 1024.0  # To move up and down between magnitudes of size

class PrePushToEndpointHook:

    version = None

    def __init__(self):
        self.version = "1.0.0"

    @staticmethod
    def check_for_large_files():
        # Now, do the checking:
        try:
            # Check if the repository size is too big
            git_repo_info = subprocess.check_output(
                ['git', "count-objects", "-v"],
                stderr=subprocess.STDOUT).decode("utf-8")
            repo_info_output = git_repo_info.splitlines()
            for git_output in repo_info_output:
                if "size" in git_output:
                    size_line = git_output
                    kib_info = size_line.split(":")
                    kib_val = int(kib_info[1].strip())
                    if (kib_val * units) >= max_repo_size * units:
                        print(
                            "The total size of your repository is greater than {repo_max_size}.".format(
                                repo_max_size=sizeof_fmt(max_repo_size * units)))
                        print("Use Onepanel datasets to store datasets or any files larger than {file_max_size}.".
                              format(file_max_size=sizeof_fmt(max_file_size * units)))
                        print("Remove any large files and bring your total repo size to under {repo_max_size} and try again.".
                            format(repo_max_size=sizeof_fmt(max_repo_size * units)))
                        sys.exit(1)
            sys.exit(0)

        except subprocess.CalledProcessError:
            # There was a problem calling "git status".
            print("Error executing git status")
            sys.exit(12)

    @staticmethod
    def ping_endpoint():
        conn = Connection()
        conn.load_credentials()
        data = {
            'version':'1',
            'data':''
        }

        # Figure out if this is a project or dataset push
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot connect to endpoint.")
            print("DETAILS." + onepanel_dir)
            exit(-1)

        project_push = True
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        if not os.path.isfile(project_file):
            project_push = False
        else:
            # Safe to ping the endpoint with project credentials
            pvc = ProjectViewController(conn)
            pvc.init_credentials_retrieval()
            url_params = '/gitlab/accounts/{account_uid}/project/{project_uid}/update'.format(
                account_uid=pvc.account_uid,project_uid=pvc.project_uid
            )
            try:
                pvc.post(data,params=url_params)
            except ValueError as e:
                print("Gitlab Update Failed.")

        if project_push == False:
            print("ERROR. Cannot connect to endpoint, unclear if this code is initialized with 'onepanel init'.")
            exit(-1)

def sizeof_fmt(num):
    """
	This function will return a human-readable filesize-string
	 like "3.5 MB" for it's given 'num'-parameter.
	From http://stackoverflow.com/questions/1094841
	"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < units:
            return "%3.1f %s" % (num, x)
        num /= units