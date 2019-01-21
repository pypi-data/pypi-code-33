import io
import json

from future.builtins import str


class UploadReportsRequest(object):
    def __init__(self, agent_data, report_file):
        self.agentData = io.StringIO(str(json.dumps(agent_data, default=lambda m: m.__dict__)))
        self.report = report_file
