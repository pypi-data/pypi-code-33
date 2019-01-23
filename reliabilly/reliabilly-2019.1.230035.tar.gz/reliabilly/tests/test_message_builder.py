from unittest import TestCase
from reliabilly.components.chat.message_builder import MessageBuilder, Payload


class MessageBuilderTests(TestCase):
    def test_get_payload_string(self):
        expected = "{0} has failed linting and testing."
        actual = Payload.get('CODE_QUALITY_WARNING', '_TITLE')
        self.assertEqual(expected, actual)

    def test_get_payload_string_fail(self):
        expected = None
        actual = Payload.get('TIGER', '_STYLE')
        self.assertEqual(expected, actual)

    def test_get_payload_empty(self):
        expected = None
        actual = Payload.get('', '')
        self.assertEqual(expected, actual)

    def test_make_attachment(self):
        message_type = 'CODE_QUALITY_SUCCESS'
        environment = {
            'JOB_NAME': 'reliabilly/platform/PR-257',
            'CHANGE_URL': 'https://github.com/wow/great',
            'CHANGE_AUTHOR_DISPLAY_NAME': 'Nathan Fielder',
            'CHANGE_TITLE': 'broke prod'
        }
        builder = MessageBuilder(message_type, environment)
        expected = [{
            'color': 'good',
            'title': Payload.CODE_QUALITY_SUCCESS_TITLE.format(
                'platform / PR-257'),
            'text': Payload.CODE_QUALITY_SUCCESS_TEXT,
            'actions': [{
                'type': 'button',
                'text': ':github: View pull request on Github',
                'url': 'https://github.com/wow/great'
            }],
            'fields': [{
                'title': 'Author',
                'value': 'Nathan Fielder',
                'short': True
            }, {
                'title': 'Description',
                'value': 'broke prod',
                'short': True
            }]
        }]
        actual = builder.make_attachment()
        self.assertEqual(expected, actual)

    def test_all_attachments(self):
        message_type = 'ALL'
        environment = {
            'JOB_NAME': 'bleh/blah/bloh',
            'CHANGE_URL': 'https://github.dev.reliabilly.com/reliabilly/blob',
            'CHANGE_AUTHOR_DISPLAY_NAME': 'Ali G',
            'CHANGE_TITLE': 'wossup britain',
            'GIT_URL': 'https://github.dev.reliabilly.com/reliabilly/platform.git',
            'GIT_COMMIT': 'abc123',
            'RUN_DISPLAY_URL': 'https://jenkins.com/job',
            'UAT_INT_TEST_TARGET': 'https://uat.example',
            'PROD_INT_TEST_TARGET': 'https://example'
        }
        builder = MessageBuilder(message_type, environment)
        expected = [{
            'title': Payload.ALL_TITLE,
            'text': Payload.ALL_TEXT,
            'actions': [{
                'type': 'button',
                'text': Payload.VIEW_GITHUB_LABEL,
                'url': environment['CHANGE_URL']
            }, {
                'type': 'button',
                'text': Payload.VIEW_LATEST_COMMIT_LABEL,
                'url': f"{environment['GIT_URL'][0:-4]}/commit/"
                       f"{environment['GIT_COMMIT']}"
            }, {
                'type': 'button',
                'text': Payload.VIEW_PIPELINE_LABEL,
                'url': environment['RUN_DISPLAY_URL']
            }, {
                'type': 'button',
                'text': Payload.VIEW_UAT_LABEL,
                'url': environment['UAT_INT_TEST_TARGET']
            }, {
                'type': 'button',
                'text': Payload.VIEW_PROD_LABEL,
                'url': environment['PROD_INT_TEST_TARGET']
            }],
            'fields': [{
                'title': 'Author',
                'value': environment['CHANGE_AUTHOR_DISPLAY_NAME'],
                'short': True
            }, {
                'title': 'Description',
                'value': environment['CHANGE_TITLE'],
                'short': True
            }]
        }]
        actual = builder.make_attachment()
        self.assertEqual(expected, actual)
