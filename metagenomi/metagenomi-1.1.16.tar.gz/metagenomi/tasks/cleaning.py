import json
from metagenomi.tasks.taskbase import MgTask


class CleaningTaskBase(object):
    def __init__(self, **kwargs):
        self.cmd_run = kwargs['cmd_run']

    def to_dict(self):
        return({k: v for k, v in vars(self).items()})


class ContaminantRemoval(CleaningTaskBase):
    def __init__(self, **kwargs):
        CleaningTaskBase.__init__(self, **kwargs)
        self.contaminants = kwargs['contaminants']
        self.total_removed_reads = kwargs['total_removed_reads']


class QualityTrimming(CleaningTaskBase):
    def __init__(self, **kwargs):
        CleaningTaskBase.__init__(self, **kwargs)
        self.total_removed_reads = kwargs['total_removed_reads']


class AdapterRemoval(CleaningTaskBase):
    def __init__(self, **kwargs):
        CleaningTaskBase.__init__(self, **kwargs)
        self.ftrimmed_reads = kwargs['ftrimmed_reads']
        self.ktrimmed_reads = kwargs['ktrimmed_reads']
        self.total_removed_reads = kwargs['total_removed_reads']
        self.trimmed_by_overlap_reads = kwargs['trimmed_by_overlap_reads']


class Cleaning(MgTask):
    def __init__(self, mgid, **kwargs):
        MgTask.__init__(self, mgid, **kwargs)
        self.total_bases = kwargs['total_bases']  # raw base count
        self.total_reads = kwargs['total_reads']  # raw read count

        if 'adapter_removal' in kwargs:
            self.adapter_removal = kwargs['adapter_removal']
        else:
            self.adapter_removal = None

        if 'contaminant_removal' in kwargs:
            self.contaminant_removal = kwargs['contaminant_removal']
        else:
            self.contaminant_removal = None

        if 'quality_trimming' in kwargs:
            self.quality_trimming = kwargs['quality_trimming']
        else:
            self.quality_trimming = None

        self.schema = {**self.schema, **{
                'total_bases': {'required': True, 'type': 'integer'},
                'total_reads': {'required': True, 'type': 'integer'},
                'adapter_removal': {'required': True, 'type': 'dict'},
                'contaminant_removal': {'required': True, 'type': 'dict'},
                'quality_trimming': {'required': True, 'type': 'dict'},
            }
        }

    def to_dict(self):
        d = dict()
        for k, v in vars(self).items():
            if isinstance(v, (ContaminantRemoval,
                              QualityTrimming,
                              AdapterRemoval)):
                d[k] = dict(v.to_dict())
            else:
                if k not in self.not_required:
                    d[k] = v
