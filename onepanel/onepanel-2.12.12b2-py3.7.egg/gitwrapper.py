""" Command line interface for the OnePanel Machine Learning platform

Wrap git commands and provide transparent integration onepanel commands with the git.
"""

import glob
import os
import subprocess
import onepanel


class GitWrapper:
    def __init__(self):
        self.HOST = os.getenv('GITLAB_GIT_HOST', 'git.onepanel.io')

    def init(self,onepanel_user_uid,gitlab_token,home, account_uid, project_uid):
        git_cmd = 'git init'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

        git_cmd = 'git remote add onepanel https://{}:{}@{}/{}/{}.git'.format(
            onepanel_user_uid,
            gitlab_token,
            self.HOST,
            account_uid,
            project_uid
        )
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()
        self.git_hook_code(home)

    def clone(self,onepanel_user_uid,gitlab_token, home, account_uid, project_uid, ext=''):
        git_cmd = 'git clone -o onepanel https://{}:{}@{}/{}/{}{}.git {}'.format(
            onepanel_user_uid,
            gitlab_token,
            self.HOST,
            account_uid,
            project_uid,
            ext,
            home
        )
        p = subprocess.Popen(git_cmd, shell=True)
        p.wait()

        return p.returncode

    def exclude(self, home, files):
        exclude_file = os.path.join(home, '.git/info/exclude')
        with open(exclude_file,'a+') as f:
            for file in files:
                f.write(file + '\n')

    def push(self, home):
        self.git_hook_code(home)
        if len(glob.glob(os.path.join(home, '*'))) < 1:
            print("Cannot proceed with operation, no files to push up.")
            exit(0)
        git_cmd = 'git push -u onepanel master'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

    def pull(self, home):
        git_cmd = 'git pull onepanel master'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()
        self.git_hook_code(home)

    def git_hook_code(self,cwd):
        git_hook_utility = onepanel.utilities.git_hook_utility.GitHookUtility()
        if git_hook_utility.safe_to_add_git_hooks(cwd):
            if git_hook_utility.check_pre_push_gitlab_update_hook(cwd) is False:
                git_hook_utility.add_pre_push_gitlab_update_hook(cwd)
            if git_hook_utility.check_pre_commit_hook(cwd) is False:
                git_hook_utility.add_pre_commit_hook(cwd)