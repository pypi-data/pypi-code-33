import os, sys, stat
import onepanel.git_hooks.pre_push as pre_push
import onepanel.git_hooks.pre_commit
from onepanel.constants import CLI_VERSION


class GitHookUtility:

    version = None

    def __init__(self):
        self.version = "1.0.0"


    @staticmethod
    def safe_to_add_git_hooks(cwd):
        # Are we in a OnePanel dataset (or project), and is the .git folder available in the current dir?
        onepanel_dir = os.path.join(cwd, '.onepanel')
        git_dir = os.path.join(cwd, '.git')
        if os.path.exists(onepanel_dir) and os.path.exists(git_dir):
            return True
        return False


    def check_pre_push_gitlab_update_hook(self, cwd):
        # Open up the "pre-push" git-hook and verify that it's our git-hook
        git_pre_push_file = os.path.join(cwd,'.git','hooks','pre-push')
        if os.path.isfile(git_pre_push_file):
            with open(git_pre_push_file,'r') as f:
                # First line should be magic shebang with python in it
                first_line_ok = False
                # Second line is an identifier for this code check
                second_line_ok = False
                # Third line is a version identifier
                third_line_ok = False
                first_line = f.readline()
                if "python" in first_line:
                    first_line_ok = True
                second_line = f.readline()
                if "onepanel-hook" in second_line:
                    second_line_ok = True
                third_line = f.readline()
                if CLI_VERSION in third_line:
                    third_line_ok = True
                if first_line_ok and second_line_ok and third_line_ok:
                    return True
        return False

    def add_pre_push_gitlab_update_hook(self, cwd):
        # Open up the "pre-push" git-hook and write our hook into it
        git_pre_push_file = os.path.join(cwd, '.git', 'hooks', 'pre-push')
        hook_itself = pre_push.PrePush.read_self()

        with open(git_pre_push_file,'w') as f:
            # Write the first line, which should be the python executable path
            f.write("#!"+sys.executable+'\n')
            # Second line should be our identifier
            f.write("#onepanel-hook"+'\n')
            # Add the version identifier, so the script can always update it with new hook code as needed
            f.write("#CLI Version:{version}".format(version=CLI_VERSION)+'\n')
            # The rest of the file should be the hook code
            f.write(hook_itself)
            # ensure file is executable
            st = os.stat(git_pre_push_file)
            os.chmod(git_pre_push_file,st.st_mode | stat.S_IEXEC)

    @staticmethod
    def check_pre_commit_hook(cwd):
        # Open up the "pre-commit" git-hook and verify that it's our git-hook
        git_pre_commit_file = os.path.join(cwd, '.git', 'hooks', 'pre-commit')
        if os.path.isfile(git_pre_commit_file):
            with open(git_pre_commit_file, 'r') as f:
                # First line should be magic shebang with python in it
                first_line_ok = False
                # Second line is an identifier for this code check
                second_line_ok = False
                # Third line is a version identifier
                third_line_ok = False
                first_line = f.readline()
                if "python" in first_line:
                    first_line_ok = True
                second_line = f.readline()
                if "onepanel-hook" in second_line:
                    second_line_ok = True
                third_line = f.readline()
                if CLI_VERSION in third_line:
                    third_line_ok = True
                if first_line_ok and second_line_ok and third_line_ok:
                    return True
        return False

    @staticmethod
    def add_pre_commit_hook(cwd):
        # Open up the "pre-commit" git-hook and write our hook into it
        git_pre_commit_file = os.path.join(cwd, '.git', 'hooks', 'pre-commit')
        hook_itself = onepanel.git_hooks.pre_commit.read_self()

        with open(git_pre_commit_file, 'w') as f:
            # Write the first line, which should be the python executable path
            f.write("#!" + sys.executable + '\n')
            # Second line should be our identifier
            f.write("#onepanel-hook" + '\n')
            # Add the version identifier, so the script can always update it with new hook code as needed
            f.write("#CLI Version:{version}".format(version=CLI_VERSION) + '\n')
            # The rest of the file should be the hook code
            f.write(hook_itself)
            # ensure file is executable
            st = os.stat(git_pre_commit_file)
            os.chmod(git_pre_commit_file, st.st_mode | stat.S_IEXEC)
