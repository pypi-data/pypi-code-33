from dateutil.parser import parse


class Metadata(object):
    def __init__(self, d):
        # type: (dict) -> None
        super(Metadata, self).__init__()
        self.d = d
        self.creation_timestamp = parse(d.get("creationTimestamp"))
        self.name = d.get("name")
        self.namespace = d.get("namespace")
        self.resource_version = d.get("resourceVersion")
        self.self_link = d.get("selfLink")
        self.uid = d.get("uid")
