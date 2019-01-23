import json

from onepanel.models.instance import Instance
from onepanel.models.volume_type import VolumeType
from onepanel.models.machine_type import MachineType
from onepanel.models.instance_template import InstanceTemplate


class APIJSONEncoder(json.JSONEncoder):
    """JSONEncoder for uploading items via API"""
    def default(self, obj):
        if isinstance(obj, Instance):
            return obj.api_json()
        if isinstance(obj, MachineType):
            return obj.api_json()
        if isinstance(obj, VolumeType):
            return obj.api_json()
        if isinstance(obj, InstanceTemplate):
            return obj.api_json()
        
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)