from probator.plugins.types.issues import BaseIssue, IssueProp


class EBSVolumeAuditIssue(BaseIssue):
    """EBSVolume audit issue"""
    issue_type = 'aws_ebs_volume_audit'
    issue_name = 'EBS Volume Audit'
    issue_properties = [
        IssueProp(key='volume_id', name='Volume ID', type='string', resource_reference=True, primary=True),
        IssueProp(key='last_notice', name='Last Notification', type='datetime', show=False),
        IssueProp(key='notes', name='Notes', type='array'),
    ]
