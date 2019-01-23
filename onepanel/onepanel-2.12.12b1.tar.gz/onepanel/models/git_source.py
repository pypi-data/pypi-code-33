from onepanel.models.api_json import APIJSON

class GitSource(APIJSON):
    def __init__(self, branch, commit_hash):
        self.version = 1
        self.branch = branch
        self.commit_hash = commit_hash

    @classmethod
    def from_json(cls, dct):
        data = dct['data']
        return cls(data['branch']['name'], data['commit']['id'])

    @classmethod
    def from_string(cls, value):
        """value is expected to be branch_name/commit_hash"""

        parts = value.split('/')

        return cls(parts[0], parts[1])

    def api_json(self):
        return {
            'version': self.version,
            'data': {
                'commit': {
                    'id': self.commit_hash
                },
                'branch': {
                    'name': self.branch
                }
            }
        }