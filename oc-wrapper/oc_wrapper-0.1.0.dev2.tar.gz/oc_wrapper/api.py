from oc_wrapper.policy import Policy
from oc_wrapper.rolebindings import RoleBindings


class Oc(object):
    ci_mode = True

    def __init__(self):
        super(Oc, self).__init__()
        self.policy = Policy(self.ci_mode)
        self.role_bindings = RoleBindings(self.ci_mode)
