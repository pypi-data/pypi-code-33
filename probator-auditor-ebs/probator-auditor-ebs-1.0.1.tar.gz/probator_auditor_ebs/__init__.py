from collections import defaultdict
from datetime import datetime

from probator.config import dbconfig
from probator.constants import ConfigOption
from probator.database import db
from probator.plugins import BaseAuditor
from probator.plugins.types.resources import EBSVolume
from probator.utils import get_template, get_resource_id, send_notification, NotificationContact

from probator_auditor_ebs.types import EBSVolumeAuditIssue


class EBSAuditor(BaseAuditor):
    name = 'EBS Auditor'
    ns = 'auditor_ebs'
    interval = dbconfig.get('interval', ns, 1440)
    options = (
        ConfigOption('enabled', False, 'bool', 'Enable the EBS auditor'),
        ConfigOption('interval', 1440, 'int', 'How often the auditor runs, in minutes'),
        ConfigOption('email_subject', 'Unattached EBS Volumes', 'string', 'Subject of the notification emails'),
        ConfigOption('ignore_tags', ['probator:ignore'], 'array', 'A list of tags that will cause the auditor to ignore the volume')
    )

    def __init__(self):
        super().__init__()
        self.subject = self.dbconfig.get('email_subject', self.ns)
        self.ignored_tags = set(dbconfig.get('ignore_tags', self.ns))

    def run(self, *args, **kwargs):
        """Main execution point for the auditor

        Args:
            *args:
            **kwargs:

        Returns:
            `None`
        """
        self.log.debug('Starting EBSAuditor')
        data = self.update_data()

        notices = defaultdict(list)
        for account, issues in data.items():
            for issue in issues:
                for recipient in account.contacts:
                    notices[NotificationContact(type=recipient['type'], value=recipient['value'])].append(issue)

        self.notify(notices)

    def update_data(self):
        """Update the database with the current state and return a dict containing the new / updated and fixed
        issues respectively, keyed by the account object

        Returns:
            `dict`
        """
        existing_issues = EBSVolumeAuditIssue.get_all()
        output = defaultdict(list)

        volumes = self.get_unattached_volumes()
        issues = self.process_new_issues(volumes, existing_issues)
        self.process_fixed_issues(volumes, existing_issues)

        for issue in issues:
            volume = EBSVolume.get(issue.volume_id)
            output[volume.account].append(issue)

        return output

    def get_unattached_volumes(self):
        """Build a list of all volumes missing tags and not ignored. Returns a `dict` keyed by the issue_id with the
        volume as the value

        Returns:
            :obj:`dict` of `str`: `EBSVolume`
        """
        volumes = {}
        for volume in EBSVolume.get_all().values():
            issue_id = get_resource_id('evai', volume.id)

            if len(volume.attachments) == 0:
                if any(tag.key in self.ignored_tags for tag in volume.tags):
                    self.log.debug(f'Ignoring unattached volume {volume.id}, ignore tag has been set')
                    continue

                volumes[issue_id] = volume

        return volumes

    def process_new_issues(self, volumes, existing_issues):
        """Return a list of new or updated issues

        Args:
            volumes (:obj:`dict` of `str`: `EBSVolume`): Dict of current volumes with issues
            existing_issues (:obj:`dict` of `str`: `EBSVolumeAuditIssue`): Current list of issues

        Returns:
            `list` of `EBSVolumeAuditIssue`
        """
        issues = []
        for issue_id, volume in volumes.items():
            if issue_id in existing_issues:
                issue = existing_issues[issue_id]

                data = {
                    'notes': issue.notes,
                    'last_notice': issue.last_notice
                }
                if issue.update_issue(data):
                    issues.append(issue)
                    db.session.add(issue.issue)
                    self.log.debug(f'Updated EBSVolumeAuditIssue for {volume.id} ({issue_id})')

            else:
                properties = {
                    'volume_id': volume.id,
                    'last_change': datetime.now(),
                    'last_notice': None,
                    'notes': []
                }

                issue = EBSVolumeAuditIssue.create(
                    issue_id=issue_id,
                    account_id=volume.account_id,
                    location=volume.location,
                    properties=properties
                )
                issues.append(issue)
                db.session.add(issue.issue)
                self.log.debug(f'Created new issue for unattached EBS volume {volume.id} ({issue_id})')

        db.session.commit()

        return issues

    def process_fixed_issues(self, volumes, existing_issues):
        """Remove fixed issues from database

        Args:
            volumes (`dict`): A dictionary keyed on the issue id, with the :obj:`Volume` object as the value
            existing_issues (`dict`): A dictionary keyed on the issue id, with the :obj:`EBSVolumeAuditIssue` object as the value

        Returns:
            :obj:`list` of :obj:`EBSVolumeAuditIssue`
        """
        for issue_id, issue in list(existing_issues.items()):
            if issue_id not in volumes:
                self.log.debug(f'Removing fixed issue {issue.id} / {issue.volume_id}')
                db.session.delete(issue.issue)

        db.session.commit()

    def notify(self, notices):
        """Send notifications to the users via. the provided methods

        Args:
            notices (:obj:`dict` of `str`: `dict`): List of the notifications to send

        Returns:
            `None`
        """
        issues_html = get_template('unattached_ebs_volume.html')
        issues_text = get_template('unattached_ebs_volume.txt')

        for recipient, issues in list(notices.items()):
            if issues:
                message_html = issues_html.render(issues=issues)
                message_text = issues_text.render(issues=issues)

                send_notification(
                    subsystem=self.name,
                    recipients=[recipient],
                    subject=self.subject,
                    body_html=message_html,
                    body_text=message_text
                )
