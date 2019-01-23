# pylint: disable=too-few-public-methods
class Payload:
    @staticmethod
    def get(base, suffix):
        try:
            string = Payload.__getattribute__(Payload, f'{base}{suffix}')
        except AttributeError:
            string = None
        return string

    ALL_TEXT = 'Debug for great success'
    ALL_TITLE = 'Very nice'
    CODE_QUALITY_WARNING_TEXT = "Unfortunately, your pull request has " \
                                "failed during the linting and testing" \
                                " phase. You'll need to fix any issues " \
                                "in order for the team to review your changes."
    CODE_QUALITY_WARNING_TITLE = "{0} has failed linting and testing."
    CODE_QUALITY_SUCCESS_TEXT = "A new pull request has successfully passed" \
                                " testing and is ready to be reviewed by a" \
                                " member of the team."
    CODE_QUALITY_SUCCESS_TITLE = "{0} is ready to be reviewed."
    CODE_QUALITY_FAILURE_MASTER_TEXT = "The master branch has failed to pass" \
                                       " a code quality check. Someone" \
                                       " should investigate how this error" \
                                       " was first introduced."
    CODE_QUALITY_FAILURE_MASTER_TITLE = CODE_QUALITY_WARNING_TITLE
    DEBUG_FAILURE_TEXT = 'Hello! Please ignore me!'
    DEBUG_FAILURE_TITLE = ':very_nice: {0} is being debugged for great success'
    DEBUG_WARNING_TEXT = DEBUG_FAILURE_TEXT
    DEBUG_WARNING_TITLE = DEBUG_FAILURE_TITLE
    DEBUG_SUCCESS_TEXT = DEBUG_FAILURE_TEXT
    DEBUG_SUCCESS_TITLE = DEBUG_FAILURE_TITLE
    DOCKER_BUILD_FAILURE_TITLE = "{0} has failed upon attempting to build " \
                                 "Docker containers"
    DOCKER_PUSH_FAILURE_TITLE = "{0} has failed upon attempting to push to ECR"
    UAT_DEPLOY_FAILURE_TITLE = "{0} has failed while trying to deploy to UAT"
    UAT_DEPLOY_SUCCESS_TITLE = "{0} has successfully deployed to UAT"
    UAT_DEPLOY_SUCCESS_TEXT = "The latest UAT deployment was successful. " \
                              "It's almost to production! :thonking:"
    UAT_INTEGRATION_FAILURE_TITLE = "{0} has failed during integration " \
                                    "testing on UAT"
    UAT_CREATE_SYNTH_FAILURE_TITLE = "{0} has failed while trying to " \
                                     "create UAT synthetic monitors " \
                                     "for New Relic"
    UAT_CREATE_SYNTH_FAILURE_TEXT = "Unfortunately something went wrong " \
                                    "while trying to attach monitors to the" \
                                    " latest UAT deployment."
    PROD_BACKUP_FAILURE_TITLE = "{0} has failed while trying to back up" \
                                " production data"
    PROD_DEPLOY_FAILURE_TITLE = "{0} has failed while trying to deploy to " \
                                "production"
    PROD_DEPLOY_SUCCESS_TITLE = ":very_nice: {0} has successfully deployed " \
                                "to production"
    PROD_DEPLOY_SUCCESS_TEXT = "Aww yeah, your latest pull request has " \
                               "safely made it all the way to production.\n" \
                               "Nice work! :b1:"
    PROD_CREATE_SYNTH_FAILURE_TITLE = "{0} has failed while trying to " \
                                      "create production synthetic monitors " \
                                      "for New Relic"
    PROD_CREATE_SYNTH_FAILURE_TEXT = "Unfortunately something went wrong " \
                                     "while trying to attach monitors to the" \
                                     " latest production deployment."
    PROD_RESTORE_FAILURE_TITLE = "{0} has failed while trying to restore" \
                                 " production backups"
    PROD_INTEGRATION_FAILURE_TITLE = "{0} has failed during integration " \
                                     "testing on production"
    LATEST_COMMIT_URL = '{0}/commit/{1}'
    VIEW_GITHUB_LABEL = ":github: View pull request on Github"
    VIEW_LATEST_COMMIT_LABEL = ":github: View latest commit"
    VIEW_PIPELINE_LABEL = ":jenkins: View Jenkins pipeline"
    VIEW_PROD_LABEL = ":do_it_live: View production environment"
    VIEW_UAT_LABEL = ":uat: View UAT environment"
    SHOW_CHANGE_AUTHOR = ['CODE_QUALITY_SUCCESS',
                          'CODE_QUALITY_FAILURE_MASTER',
                          'DOCKER_BUILD_FAILURE', 'DOCKER_PUSH_FAILURE',
                          'UAT_DEPLOY_FAILURE', 'UAT_INTEGRATION_FAILURE',
                          'PROD_BACKUP_FAILURE', 'PROD_RESTORE_FAILURE',
                          'PROD_INTEGRATION_FAILURE', 'ALL']
    SHOW_PULL_REQUEST_TITLE = ['CODE_QUALITY_SUCCESS',
                               'PROD_DEPLOY_SUCCESS', 'ALL']
    SHOW_LATEST_COMMIT_BUTTON = ['CODE_QUALITY_FAILURE_MASTER',
                                 'DOCKER_BUILD_FAILURE',
                                 'DOCKER_PUSH_FAILURE',
                                 'UAT_DEPLOY_FAILURE',
                                 'UAT_INTEGRATION_FAILURE',
                                 'PROD_CREATE_SYNTH_FAILURE',
                                 'PROD_BACKUP_FAILURE',
                                 'PROD_RESTORE_FAILURE',
                                 'PROD_INTEGRATION_FAILURE', 'ALL']
    SHOW_PULL_REQUEST_BUTTON = ['CODE_QUALITY_WARNING',
                                'CODE_QUALITY_SUCCESS', 'ALL']
    SHOW_PIPELINE_BUTTON = ['CODE_QUALITY_WARNING',
                            'CODE_QUALITY_FAILURE_MASTER',
                            'DOCKER_BUILD_FAILURE', 'DOCKER_PUSH_FAILURE',
                            'UAT_DEPLOY_FAILURE', 'UAT_INTEGRATION_FAILURE',
                            'PROD_BACKUP_FAILURE', 'PROD_DEPLOY_FAILURE',
                            'PROD_RESTORE_FAILURE',
                            'PROD_CREATE_SYNTH_FAILURE',
                            'PROD_INTEGRATION_FAILURE',
                            'PROD_DEPLOY_SUCCESS', 'ALL']
    SHOW_PROD_BUTTON = ['PROD_INTEGRATION_FAILURE', 'PROD_DEPLOY_SUCCESS',
                        'ALL']
    SHOW_UAT_BUTTON = ['UAT_INTEGRATION_FAILURE', 'UAT_DEPLOY_SUCCESS', 'ALL']


class MessageBuilder:
    def __init__(self, message_type, environment):
        self.message_type = message_type
        self.env = environment

    def make_attachment(self):
        attachment = dict()
        fields = list()
        actions = list()

        job_name = self.env.get('JOB_NAME')
        repo_and_branch = ' / '.join(job_name.split('/')[1:])

        attachment['title'] = Payload.get(
            self.message_type, '_TITLE').format(repo_and_branch)

        if Payload.get(self.message_type, '_TEXT'):
            attachment['text'] = Payload.get(self.message_type, '_TEXT')

        if 'FAILURE' in self.message_type:
            attachment['color'] = 'danger'
        if 'WARNING' in self.message_type:
            attachment['color'] = 'warning'
        if 'SUCCESS' in self.message_type:
            attachment['color'] = 'good'

        if self.message_type in Payload.SHOW_CHANGE_AUTHOR:
            fields.append({
                'title': 'Author',
                'value': self.env.get('CHANGE_AUTHOR_DISPLAY_NAME'),
                'short': True
            })

        if self.message_type in Payload.SHOW_PULL_REQUEST_TITLE:
            fields.append({
                'title': 'Description',
                'value': self.env.get('CHANGE_TITLE'),
                'short': True
            })

        if self.message_type in Payload.SHOW_PULL_REQUEST_BUTTON:
            actions.append({
                'type': 'button',
                'text': Payload.VIEW_GITHUB_LABEL,
                'url': self.env.get('CHANGE_URL')
            })

        if self.message_type in Payload.SHOW_LATEST_COMMIT_BUTTON:
            actions.append({
                'type': 'button',
                'text': Payload.VIEW_LATEST_COMMIT_LABEL,
                'url': Payload.LATEST_COMMIT_URL.format(
                    self.env.get('GIT_URL')[0:-4], self.env.get('GIT_COMMIT'))
            })

        if self.message_type in Payload.SHOW_PIPELINE_BUTTON:
            actions.append({
                'type': 'button',
                'text': Payload.VIEW_PIPELINE_LABEL,
                'url': self.env.get('RUN_DISPLAY_URL')
            })

        if self.message_type in Payload.SHOW_UAT_BUTTON:
            actions.append({
                'type': 'button',
                'text': Payload.VIEW_UAT_LABEL,
                'url': self.env.get('UAT_INT_TEST_TARGET')
            })

        if self.message_type in Payload.SHOW_PROD_BUTTON:
            actions.append({
                'type': 'button',
                'text': Payload.VIEW_PROD_LABEL,
                'url': self.env.get('PROD_INT_TEST_TARGET')
            })

        attachment['actions'] = actions
        attachment['fields'] = fields
        return [attachment]
