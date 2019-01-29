from typing import List

from oc_wrapper.model.Metadata import Metadata


class RoleBinding(object):

    def __init__(self, d):
        # type: (dict) -> None
        super(RoleBinding, self).__init__()
        self.d = d
        self.api_version = d.get("apiVersion")
        self.group_names = d.get("groupNames")
        self.metadata = Metadata(d.get("metadata"))
        self.role_ref = RoleRef(d.get("roleRef"))
        self.subjects = Subject.from_dist_list(d.get("subjects"))

    def __repr__(self):
        return "Binding {n}@{ns} (UID: {uid}) between role '{r}' and groups {g}.".format(
            n=self.metadata.name,
            ns=self.metadata.namespace,
            uid=self.metadata.uid,
            r=self.role_ref.name,
            g=self.group_names
        )


class RoleRef(object):

    def __init__(self, d):
        # type: (dict) -> None
        super(RoleRef, self).__init__()
        self.d = d
        self.name = d.get("name")


class Subject(object):

    def __init__(self, d):
        # type: (dict) -> None
        super(Subject, self).__init__()
        self.d = d
        self.kind = d.get("kind")
        self.name = d.get("name")

    @staticmethod
    def from_dist_list(l):
        # type: (List[dict]) -> [Subject]
        return [Subject(s) for s in l]
