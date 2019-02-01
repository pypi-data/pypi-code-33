from probator.plugins.types.issues import BaseIssue, IssueProp


class RequiredTagsIssue(BaseIssue):
    """Issue type for instances missing required tags"""
    issue_type = 'aws_required_tags'
    issue_name = 'Required Tags'
    issue_properties = [
        IssueProp(key='resource_id', name='Resource ID', type='string', resource_reference=True, primary=True),
        IssueProp(key='resource_type', name='Resource Type', type='int'),
        IssueProp(key='state', name='State', type='string', show=False),
        IssueProp(key='shutdown_on', name='Shutdown on', type='datetime'),
        IssueProp(key='missing_tags', name='Missing Tags', type='array'),
        IssueProp(key='notes', name='Notes', type='array'),
    ]
