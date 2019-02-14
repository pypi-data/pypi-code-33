import subprocess


class CheckGitLfsInstalled:
    git_major_vr = 0
    git_sub_vr = 0
    git_minor_vr = 0

    def __init__(self):
        self.git_installed = False

    def figure_out_git_installed(self):
        shell_cmd = ['git','version']
        try:
            p = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=False)
            p.wait()
            line = p.stdout.readline()
            git_output = line.decode().rstrip()
            if "git version" in git_output:
                self.git_installed = True
                # Figure out the git version installed
                self.parse_git_version(git_output)
        except BaseException:
            print("An error occurred when trying to figure out if git is installed.")

    def parse_git_version(self, shell_str):
        split_list = shell_str.split(" ")
        if len(split_list) == 3:
            git_version = split_list[2]
            git_version_list = git_version.split(".")
            # Example: "2.17.0"
            if len(git_version_list) >= 3:
                self.git_major_vr = int(git_version_list[0])
                self.git_sub_vr = int(git_version_list[1])
                self.git_minor_vr = int(git_version_list[2])

    def get_git_clone_str(self):
        return 'git clone'