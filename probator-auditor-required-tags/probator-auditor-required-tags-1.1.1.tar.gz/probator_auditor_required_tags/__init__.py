import re
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta

from more_itertools import first
from pkg_resources import iter_entry_points
from probator import PROBATOR_PLUGINS
from probator.config import dbconfig, DBCChoice
from probator.constants import ConfigOption
from probator.database import db
from probator.plugins import BaseAuditor
from probator.plugins.types.resources import BaseResource
from probator.utils import get_resource_id, NotificationContact, get_template, send_notification
from probator_auditor_required_tags.constants import DEFAULT_ALERT_CONFIG, DEFAULT_AUDIT_SCOPES, IssueAction, ResourceTypeIssues
from probator_auditor_required_tags.types import RequiredTagsIssue
from pytimeparse import parse as parse_time


class RequiredTagsAuditor(BaseAuditor):
    name = 'Required Tags Compliance'
    ns = 'auditor_required_tags'
    interval = dbconfig.get('interval', ns, 30)
    confirm_shutdown = dbconfig.get('confirm_shutdown', ns, True)
    required_tags = []
    collect_only = None
    start_delay = 0
    options = (
        ConfigOption('alert_settings', DEFAULT_ALERT_CONFIG, 'json', 'Alerting and action schedule'),
        ConfigOption('audit_ignore_tag', 'probator:ignore', 'string', 'Do not audit resources have this tag set'),
        ConfigOption('audit_scopes', DEFAULT_AUDIT_SCOPES, 'choice', 'Select the services you would like to audit'),
        ConfigOption('collect_only', True, 'bool', 'Do not shutdown instances, only update caches'),
        ConfigOption('email_subject', 'Required tags audit notification', 'string', 'Subject of the email notification'),
        ConfigOption('enabled', False, 'bool', 'Enable the Required Tags auditor'),
        ConfigOption('grace_period', 4, 'int', 'Only process resources older than N hours'),
        ConfigOption('interval', 30, 'int', 'How often the auditor executes, in minutes.'),
    )

    def __init__(self):
        super().__init__()
        self.log.debug('Starting RequiredTags auditor')
        type_plugins = PROBATOR_PLUGINS['probator.plugins.types']['plugins']

        self.alert_settings = dbconfig.get('alert_settings', self.ns)
        self.audit_ignore_tag = dbconfig.get('audit_ignore_tag', self.ns)
        self.audit_scopes = dbconfig.get('audit_scopes', self.ns).get('enabled', [])
        self.collect_only = dbconfig.get('collect_only', self.ns, True)
        self.email_subject = dbconfig.get('email_subject', self.ns, 'Required tags audit notification')
        self.grace_period = dbconfig.get('grace_period', self.ns, 4)

        filtered_scopes = filter(lambda scope: scope.name in self.audit_scopes, type_plugins)
        self.audited_resource_types = {ep.name: ep.load() for ep in filtered_scopes}

        # Build list of all available action functions
        self.functions = {ep.name: ep for ep in iter_entry_points('probator_auditor_required_tags.actions')}

    @staticmethod
    def bootstrap():
        """Bootstrap plugin configuration items"""
        if not RequiredTagsAuditor.bootstrapped:
            dbconfig.reload_data()
            resource_types = [rt.resource_type for rt in db.ResourceType.all()]
            cfg_item = dbconfig.get('audit_scopes', RequiredTagsAuditor.ns)

            selected = list(filter(lambda rt: rt in resource_types, cfg_item.get('enabled', []))) if cfg_item else []
            dbconfig.set(
                namespace=RequiredTagsAuditor.ns,
                key='audit_scopes',
                value=DBCChoice({
                    'enabled': selected,
                    'available': resource_types,
                    'max_items': len(resource_types),
                    'min_items': 0
                }),
            )

            RequiredTagsAuditor.bootstrapped = True

    def run(self):
        """Execute the auditor

        Returns:
            `None`
        """
        existing_issues = RequiredTagsIssue.get_all()
        new_issues = []
        updated_issues = []
        fixed_issues = []

        if not self.audited_resource_types:
            self.log.warning('No resource types enabled in `audit_scope`, auditor will have no effect')
            return

        for type_name, cls in self.audited_resource_types.items():
            issues = self.resource_type_issues(cls, existing_issues)
            new_issues += issues.new
            updated_issues += issues.updated

        existing_issue_keys = set(existing_issues.keys())
        current_issue_keys = {x.issue.id for x in new_issues} | {x.issue.id for x in updated_issues}

        for issue_id in existing_issue_keys - current_issue_keys:
            issue = existing_issues[issue_id]
            resource = BaseResource.get(issue.resource_id)
            if resource:
                fixed_issues.append(resource)
            else:
                self.log.debug(f'Issue {issue_id} refers to a removed resource {issue.resource_id}, silently ignoring')

            db.session.delete(issue.issue)
        db.session.commit()

        self.handle_actions(issues=updated_issues)
        self.notify(
            new_issues=new_issues,
            updated_issues=updated_issues,
            fixed_issues=fixed_issues
        )

    def get_action_config_for_class(self, resource_type_name):
        """Return the computed alert configuration for a given resource type

        Args:
            resource_type_name (`str`): Name of the resource class

        Returns:
            `dict` - Returns an alert configuration dictionary
        """
        config = deepcopy(self.alert_settings['global'])
        resource_config = deepcopy(self.alert_settings.get(resource_type_name, {}))
        config['requiredTags'].update(resource_config.get('requiredTags', {}))
        config['extraConfig'].update(resource_config.get('extraConfig', {}))

        if 'actions' in resource_config:
            config['actions'] = resource_config['actions']

        for sched in config['actions']:
            sched['age'] = parse_time(sched['age'])

        return config

    def get_next_action(self, resource_class, issue):
        """Return the next action to perform

        Args:
            resource_class (`BaseResource`): Resource class for issue
            issue (`RequiredTagsIssue`): Full action schedule for resource type

        Returns:
            `dict`, `None`
        """
        schedule = self.get_action_config_for_class(resource_class.resource_type).get('actions', {})
        current = first(filter(lambda x: x['name'] == issue.state, schedule), default=None)
        return first(filter(lambda x: x['order'] == current['order'] + 1, schedule), default=None) if current else None

    def resource_type_issues(self, resource_class, existing_issues):
        """Return a list of resources missing required tags

        Args:
            resource_class (`BaseResource`): Class of resource type to gather
            existing_issues (`list` of `RequiredTagsIssue`): List of existing issues

        Returns:
            `dict` - Dictionary of all discovered issues
        """
        new_issues = []
        updated_issues = []

        resources = resource_class.get_all()
        grace_time = datetime.now() - timedelta(hours=self.grace_period)
        config = self.get_action_config_for_class(resource_class.resource_type)

        for resource_id, resource in resources.items():
            missing_tags = []
            notes = []

            # Resource was deleted, treat issue as fixed without alerting
            if not resource:
                continue

            resource_tags = {tag.key: tag.value for tag in resource.tags}

            for key, pattern in config['requiredTags'].items():
                if key not in resource_tags:
                    missing_tags.append(key)

                else:
                    if pattern:
                        if not re.search(pattern, resource_tags[key]):
                            missing_tags.append(key)
                            notes.append(f'Tag "{key}" exists but does not have a valid value')

            if missing_tags:
                properties = {
                    'resource_id': resource.id,
                    'missing_tags': missing_tags,
                    'notes': notes,
                    'resource_type': resource_class.resource_type,
                }
                issue_id = get_resource_id('reqtag', resource.id)

                if issue_id in existing_issues:
                    issue = existing_issues[issue_id]
                    next_action = self.get_next_action(resource_class, issue)

                    # If there's no other actions to take after the current, leave the issue as is
                    if next_action:
                        next_action_time = issue.created + timedelta(seconds=next_action['age'])
                        if datetime.now() > next_action_time and not self.collect_only:
                            properties['state'] = next_action['name']
                            updated_issues.append(IssueAction(issue=issue, resource=resource))

                        else:
                            updated_issues.append(IssueAction(issue=issue, resource=resource, alert=False))

                        if issue.update_issue(properties=properties):
                            db.session.add(issue.issue)
                    else:
                        updated_issues.append(IssueAction(issue=issue, resource=resource, alert=False))
                else:
                    resource = resource_class.get(properties['resource_id'])
                    if resource.created > grace_time:
                        self.log.debug(f'Skipping {resource.id} as it is within the grace period')
                        continue

                    shutdown_age = first(filter(lambda x: x['action'] == 'stop', config['actions']))

                    if resource.created < grace_time:
                        properties.update({
                            'state': 'alert:1',
                            'shutdown_on': datetime.now() + timedelta(seconds=shutdown_age['age'])
                        })

                        issue = RequiredTagsIssue.create(
                            issue_id=issue_id,
                            properties=properties,
                            account_id=resource.account_id,
                            location=resource.location
                        )
                        db.session.add(issue.issue)
                        new_issues.append(IssueAction(issue=issue, resource=resource))

                        self.log.debug(f'Added new required tags issue for {resource}')

        db.session.commit()

        return ResourceTypeIssues(new=new_issues, updated=updated_issues)

    def get_state_action(self, *, resource_type, issue_state):
        """Return the action for a given state

        Args:
            resource_type (`str`): Resource type name
            issue_state (`str`): Issue state name

        Returns:
            `str`
        """
        config = self.get_action_config_for_class(resource_type)
        for action in config['actions']:
            if action['name'] == issue_state:
                return action['action']

        return None

    def handle_actions(self, *, issues):
        """Perform audit actions (stop / remove)

        Args:
            issues (`list` of `IssueAction`): List of issues

        Returns:
            `None`
        """
        for issue_data in issues:
            action_name = self.get_state_action(resource_type=issue_data.resource.resource_type, issue_state=issue_data.issue.state)
            if action_name in ('stop', 'remove'):
                func_name = f'{issue_data.resource.resource_type}_{action_name}'

                if func_name in self.functions:
                    func = self.functions[func_name].load()
                    func(issue_data.resource)
                else:
                    self.log.warning(f'Unable to find action {action_name}')

    def notify(self, *, new_issues, updated_issues, fixed_issues):
        """Notify users, if needed

        Args:
            new_issues (`list` of `IssueAction`): List of new issues
            updated_issues (`list` of `IssueAction`): List of existing / updated issues
            fixed_issues (`list` of `BaseResource`): List of resources whose issues were fixed

        Returns:
            `None`
        """
        html_tmpl = get_template('required_tags_notice.html')
        text_tmpl = get_template('required_tags_notice.txt')
        contacts = defaultdict(lambda: {'issues': [], 'fixed': []})
        issues = new_issues + updated_issues

        for data in filter(lambda x: x.alert, issues):
            issue_contacts = BaseResource.get(data.resource.id).get_contacts()
            for contact in map(NotificationContact.get, issue_contacts):
                contacts[contact]['issues'].append(data)

        for resource in fixed_issues:
            issue_contacts = resource.get_contacts()
            for contact in map(NotificationContact.get, issue_contacts):
                contacts[contact]['fixed'].append(resource)

        for contact, data in contacts.items():
            html_body = html_tmpl.render(issues=data['issues'], fixed=data['fixed'])
            text_body = text_tmpl.render(issues=data['issues'], fixed=data['fixed'])

            send_notification(
                subsystem=self.ns,
                recipients=[contact],
                subject=self.email_subject,
                body_html=html_body,
                body_text=text_body
            )
