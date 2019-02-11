class Project:
    def __init__(self, name, version):
        self.name = name
        self.version = version


class Job:
    def __init__(self, name, number=0, branch=None):
        self.name = name
        self.number = number
        self.branch = branch

	
class CustomField:
    def __init__(self, key, value):
        self.dict = {key: value}
        self.value = value
	self.key = key
