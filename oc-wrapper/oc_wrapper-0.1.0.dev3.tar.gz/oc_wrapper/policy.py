import os
import subprocess


class Policy(object):

    def __init__(self, ci_mode=True):
        super(Policy, self).__init__()
        self.ci_mode = ci_mode

    def add_role_to_group(self, role, group, namespace):
        cmd = ['oc', 'policy', 'add-role-to-group', role, group, '-n', namespace]
        cmd_str = ' '.join(cmd)
        print("Calling: '{}'.".format(cmd_str))

        if self.ci_mode:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        else:
            os.system(cmd_str)
