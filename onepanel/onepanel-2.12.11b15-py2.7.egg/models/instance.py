import datetime
import json

import iso8601

from onepanel.models.util import parse_date, format_timedelta
from onepanel.models.machine_type import MachineType
from onepanel.models.volume_type import VolumeType
from onepanel.models.account import Account
from onepanel.models.project import Project
import onepanel.models.instance_template as instanceTemplate
from onepanel.models.instance_template import InstanceTemplate

# TODO dataset mounts and source code
class Instance:
    INSTANCE_STATE_CREATED  = 'created'
    INSTANCE_STATE_STARTING = 'starting'
    INSTANCE_STATE_STARTED  = 'started'
    INSTANCE_STATE_READY    = 'ready'
    INSTANCE_STATE_PAUSED   = 'paused'
    INSTANCE_STATE_RESUMING = 'resuming'
    INSTANCE_STATE_RESUMED  = 'resumed'

    def __init__(self):
        self.uid = None
        self.createdAt = None
        self.launchedAt = None
        self.startedAt = None
        self.readyAt = None
        self.lastStoppedAt = None
        self.active = False
        self.project = Project()
        self.machineType = MachineType()
        self.volumeType = VolumeType()
        self.instanceTemplate = InstanceTemplate()

    @classmethod
    def from_json(cls, dct):
        instance = cls()

        instance.uid = dct['uid']
        instance.createdAt = parse_date(dct['createdAt'])
        instance.launchedAt = parse_date(dct['launchedAt'])
        instance.startedAt = parse_date(dct['startedAt'])
        instance.readyAt = parse_date(dct['readyAt'])
        instance.lastStoppedAt = parse_date(dct['lastStoppedAt'])
        instance.active = dct['active']
        instance.project = Project.from_json(dct['project'])
        instance.machineType = MachineType.from_json(dct['machineType'])
        instance.volumeType = VolumeType.from_json(dct['volumeType'])
        instance.instanceTemplate = instanceTemplate.from_json(dct['instanceTemplate'])

        return instance

#TODO document
    def simple_view(self):
        info = self.machineType.info

        item = {
            'account_uid': self.project.account.uid,
            'project_uid': self.project.uid,
            'uid': self.uid,
            'cpu': info['cpu'],
            'gpu': info['gpu'],
            'ram': info['ram'],
            'hdd': self.volumeType.info['size'],
            'duration_ready': format_timedelta(self.duration_ready()),
            'age': format_timedelta(self.age()),
            'state': self.state()
        }

        return item

    def state(self):
        if not self.active:
            if self.lastStoppedAt is not None:
                return Instance.INSTANCE_STATE_PAUSED

            return Instance.INSTANCE_STATE_CREATED

        if self.readyAt is not None:
            return Instance.INSTANCE_STATE_READY

        if self.startedAt is not None:
            if self.lastStoppedAt is not None:
                return Instance.INSTANCE_STATE_RESUMED

            return Instance.INSTANCE_STATE_STARTED

        if self.lastStoppedAt is not None:
            return Instance.INSTANCE_STATE_RESUMING

        return Instance.INSTANCE_STATE_STARTING
    
    def duration_ready(self, when=None):
        """How long the instance has been ready for. This is calculated from the last time it was 
           marked ready to when."""
        if when is None:
            when = datetime.datetime.now(datetime.timezone.utc)

        if self.readyAt is None:
            return datetime.timedelta(0)

        return when - self.readyAt

    def age(self, when=None):
        """How long the instance has been created to when"""
        if when is None:
            when = datetime.datetime.now(datetime.timezone.utc)

        if self.createdAt is None:
            return datetime.timedelta(0)

        return when - self.createdAt

# TODO from simple view extra method
    def api_json(self):
        return {
            'uid': self.uid,
            'machineType': self.machineType,
            'volumeType': self.volumeType,
            'instanceTemplate': self.instanceTemplate
        }