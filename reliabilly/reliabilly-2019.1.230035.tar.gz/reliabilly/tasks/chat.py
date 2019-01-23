import os
from invoke import task
from reliabilly.components.chat.chat_client import ChatClient
from reliabilly.components.chat.message_builder import MessageBuilder
from reliabilly.components.tools.source_control_client import SourceControlClient
from reliabilly.settings import Constants

CHANNEL_NAME = '#slack-channel'


@task
def populate_pull_info(_):
    """ Add pull request details to environment """
    org = Constants.GITHUB_ORG
    repo = Constants.GITHUB_REPO
    branch = os.environ.get('BRANCH_NAME', None)
    commit = os.environ.get('GIT_COMMIT', None)
    source_control_token = os.environ.get('SOURCE_CLIENT_TOKEN', None)
    if branch is not None and branch == Constants.PROD_BRANCH_NAME and source_control_token is not None:
        source_client = SourceControlClient(source_control_token)
        pull = source_client.get_origin_pr(org, repo, commit)
        if not pull:
            return
        title = str(pull.title).replace(' ', '\\ ')
        name = str(pull.user.name).replace(' ', '\\ ')
        url = str(pull.html_url)
        email = str(pull.user.email)
        merged_name = str(pull.merged_by.name).replace(' ', '\\ ')
        merged_email = str(pull.merged_by.email).replace(' ', '\\ ')
        export = 'export CHANGE_TITLE="{0}" CHANGE_AUTHOR_DISPLAY_NAME="{1}" CHANGE_URL="{2}" ' \
                 'CHANGE_AUTHOR_EMAIL="{3}" CHANGE_MERGED_BY="{4}" CHANGE_MERGED_BY_EMAIL="{5}"'.format(
                     title, name, url, email, merged_name, merged_email)
        print(export)
        return


@task
def send_channel_message(_, channel_name, message):
    """ Send slack message to a channel"""
    ChatClient().send_room_message(channel_name, message)


@task
def send_direct_message(_, email, message):
    """ Send slack message to a user"""
    ChatClient().send_user_message(email, message)


@task
def send_pipeline_message(_, message_type, alert_type):
    """ Send a Slack message with info from Jenkins pipeline"""
    environment = os.environ
    builder = MessageBuilder(message_type, environment)
    email = environment.get('CHANGE_AUTHOR_EMAIL', '')
    message = "Jenkins has an update: "
    attachments = builder.make_attachment()
    if alert_type == 'ALERT_USER':
        ChatClient().send_user_message(email, message, attachments=attachments)
    else:
        ChatClient().send_room_message(CHANNEL_NAME, message, attachments=attachments)
