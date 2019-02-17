#!/usr/bin/env python
import logging
import logging.handlers
import os
import re
import shutil
import tempfile
import threading
import time
import traceback
from urllib.parse import urljoin, urlparse

import click as click
import validictory
import yaml
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from html2text import html2text
from jira import JIRA
from msrest.authentication import BasicAuthentication
from vsts.build.v4_0.models import JsonPatchOperation
from vsts.vss_connection import VssConnection
from vsts.work_item_tracking.v4_1.models import Wiql
from vstsclient.vstsclient import VstsClient

SCHEMA_GLOBAL = {
    "type": "object",
    "properties": {
        "jira": {
            "type": "object",
            "required": False,
            "properties": {
                "url": {
                    "type": "string",
                    "required": True,
                },
                "username": {
                    "type": "string",
                    "required": True,
                },
                "password": {
                    "type": "string",
                    "required": True,
                },
                "add_hours": {
                    "type": "integer",
                    "required": True,
                },
                "skip_large_attachments": {
                    "type": "boolean",
                    "required": True,
                }
            },
        },
        "vsts": {
            "type": "object",
            "required": False,
            "properties": {
                "access_token": {
                    "type": "string",
                    "required": True,
                },
                "url": {
                    "type": "string",
                    "required": True,
                }

            },
        },
        "projects": {
            "required": True,
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "last_sync": {
                            "type": ["string", "null"],
                            "required": False,
                        },
                        "active": {
                            "type": "boolean",
                            "required": True,
                        },
                        "name": {
                            "type": "string",
                            "required": True,
                        },
                        "type": {
                            "type": "string",
                            "required": True,
                            "enum": ['task', 'issue', 'feature', 'requirement'],
                        },
                        "move_state": {
                            "type": "boolean",
                            "required": True,
                        },
                        "default_values": {
                            "required": True,
                            "type": "object",
                            "patternProperties": {
                                "System.State": {
                                    "type": "string",
                                    "required": True,
                                    "enum": ['New', 'Proposed'],
                                },
                                ".*": {
                                    "type": "string",
                                },

                            }
                        },
                        "states": {
                            "type": "array",
                            "required": True,
                        },
                    },

                },
            },
        },
        "states": {
            "required": True,
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "string",
                },
            },
        },

    }
}


def _create_work_item_field_patch_operation(op, field, value):
    if field.startswith('/'):
        path = field
    else:
        path = '/fields/{field}'.format(field=field)
    patch_operation = JsonPatchOperation()
    patch_operation.op = op
    patch_operation.path = path
    patch_operation.value = value
    return patch_operation


def __validate_and_get_data(config, logger, validate):
    content = open(config, 'r').read()
    try:
        content = yaml.load(content)
        validictory.validate(content, SCHEMA_GLOBAL)
    except:
        if validate:
            click.secho(traceback.format_exc())
        logger.error(traceback.format_exc())
        raise click.Abort()
    logger.info('Format of the config file is valid')
    if validate:
        click.echo('Format of the config file is valid')
    return content


def __get_logger(logfile):
    logger = logging.getLogger('jira2vsts')
    logger.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(logfile, 'a', 1000000, 10)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def __update_config_file(config, data):
    f = open(config, 'w+')
    f.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    f.close()


def _str_to_html(text):
    return text.replace("\n", "<br />").replace("\r", "<br />")


@click.command()
@click.option('--validate', '-v', is_flag=True, default=False, type=click.BOOL)
@click.option('--logfile', '-l',
              type=click.Path(file_okay=True, dir_okay=False, writable=True, readable=True, resolve_path=True,
                              allow_dash=True), required=True, help="Path to logfile")
@click.option('--config', '-c',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True, readable=True,
                              resolve_path=True, allow_dash=True), required=True, help="Path to the configuration file")
@click.option('--loop-every', type=click.INT, default=0, help="Loop every X minutes")
@click.option('--send', '-s', 'issue_to_send', type=click.STRING, default=False,
              help="Send one jira issue by code, format: jira_issue_code,vsts_project_name")
@click.pass_context
def cli(ctx, validate, logfile, config, loop_every, issue_to_send):
    """CLI for Jira2Vsts"""
    logger = __get_logger(logfile)
    while True:
        try:
            _main(ctx, validate, logger, config, issue_to_send)
        except:
            logger.error(traceback.format_exc())
        if loop_every:
            time.sleep(loop_every * 60)
        else:
            break


def __process_project(logger, config, data, old_client, wit_client, jira, jira_project, PROJECTS, STATES, JIRA_BROWSE,
                      issue_to_send):
    start = time.time()
    vsts_default_values = PROJECTS[jira_project].get('default_values', {})
    LAST_SYNC = PROJECTS[jira_project].get('last_sync')
    LAST_UPDATED = False
    PROJECT_STATES = PROJECTS[jira_project].get('states', [])
    JIRA_ADD_HOURS = data['jira']['add_hours']
    vsts_project = PROJECTS[jira_project]['name']
    vsts_type = PROJECTS[jira_project]['type']
    move_state = PROJECTS[jira_project]['move_state']
    SKIP_LARGE_ATTACHMENTS = data['jira']['skip_large_attachments']
    issue_to_send, vsts_destination_issue = issue_to_send.split(',', 2) if issue_to_send else (None, None)
    if vsts_destination_issue and vsts_destination_issue != vsts_project:
        logger.warning('%s - the destination project is not the same [%s] vs [%s]', jira_project,
                       vsts_destination_issue, vsts_project)
        return
    nbr_issues = 0
    logger.info('%s - starting jira project [%s] to [%s]', jira_project, jira_project, vsts_project)
    logger.info('%s - last sync is : %s', jira_project, LAST_SYNC)
    if issue_to_send:
        jira_issues = [jira.issue(issue_to_send)]
    elif LAST_SYNC:
        last_sync_formatted = (parse(LAST_SYNC) + relativedelta(hours=JIRA_ADD_HOURS)).strftime('%Y/%m/%d %H:%M')
        logger.info('%s - search for issues updated after %s', jira_project, last_sync_formatted, )
        _query = 'project=%s AND updated > "%s" ORDER BY updated ASC, createdDate ASC' % (
            jira_project, last_sync_formatted)
        jira_issues = jira.search_issues(_query)
    else:
        jira_issues = jira.search_issues('project=%s ORDER BY updated ASC, createdDate ASC' % jira_project)
    JIRA_ITEMS = list({j.key for j in jira_issues})
    logger.info('%s - jira issues to send : %s', jira_project, JIRA_ITEMS)
    tmpdir = os.path.join(tempfile.gettempdir(), 'jira2vsts', jira_project)
    try:
        os.makedirs(tmpdir)
    except:
        pass
    for jira_item in jira_issues:
        jira_item = jira_item.key
        nbr_issues += 1
        issue = jira.issue(jira_item)
        if not issue_to_send and (LAST_SYNC and issue.fields.updated <= LAST_SYNC):
            logger.warning('%s - skip [%s] because is already sent', jira_project, jira_item)
            continue
        issue_title = "{} / {}".format(jira_item, issue.fields.summary)
        updated = parse(issue.fields.updated).strftime('%d/%m/%Y %H:%M')
        if LAST_UPDATED and parse(LAST_UPDATED).strftime("%Y%m%d") < parse(issue.fields.updated).strftime("%Y%m%d"):
            PROJECTS[jira_project]['last_sync'] = LAST_UPDATED
            __update_config_file(config, data)
            logger.info("%s - set last sync to %s", jira_project, LAST_UPDATED)
        LAST_UPDATED = issue.fields.updated
        issue_description = """URL: <a href="{url}" target="_blank">{url}</a>
    State: {f.status.name}
    Reporter: {f.reporter}
    Assigned To: {f.assignee.displayName}
    Update: {updated}

    <strong><u>ORIGINAL MESSAGE:</u></strong>
    {f.description}
                """.format(i=issue, f=issue.fields, url=JIRA_BROWSE % jira_item, updated=updated)
        issue_description_comments = []
        for jira_comment in issue.fields.comment.comments:
            jira_comment = _str_to_html(
                "<strong>Date :</strong> {dt}\n<strong>Author :</strong> {author}\n<strong>Message : </strong>{body}""".format(
                    dt=parse(jira_comment.raw['updated']).strftime('%d/%m/%Y %H:%M'),
                    author=jira_comment.raw['author']['displayName'],
                    body=jira_comment.raw['body']
                ))
            issue_description_comments.append(jira_comment)
        if issue_description_comments:
            issue_description += """\n<strong><u>ORIGINAL COMMENTS:</u></strong>\n"""
            issue_description += "\n\n".join(issue_description_comments)
        issue_description = _str_to_html(issue_description)
        wiql = Wiql(
            query="""
                            SELECT [System.Id]
                            FROM WorkItems
                            WHERE 
                            [System.Title] contains "%s" AND
                            [System.TeamProject] = "%s"
                            """ % (jira_item, vsts_project)
        )
        wiql_results = wit_client.query_by_wiql(wiql).work_items
        work_items = (
            wit_client.get_work_item(int(res.id)) for res in wiql_results
        )
        try:
            vsts_id = False
            for work_item in work_items:
                workitem_name = work_item.fields.get('System.Title', '')
                if workitem_name and workitem_name.split('/')[0].strip() == jira_item and work_item.fields[
                    'System.TeamProject'] == vsts_project:
                    vsts_id = work_item.id
            document = []
            document.append(
                _create_work_item_field_patch_operation('add', 'System.Description', issue_description))
            if not vsts_id:
                document.append(_create_work_item_field_patch_operation('add', 'System.Title', issue_title))
                logger.info('%s - create a new work item from %s  with state=%s', jira_project, jira_item,
                            STATES.get(issue.fields.status.name))

                for default_key, default_value in vsts_default_values.items():
                    document.append(_create_work_item_field_patch_operation('add', default_key, default_value))
                workitem = wit_client.create_work_item(project=vsts_project, type=vsts_type, document=document)
                vsts_id = workitem.id
                logger.info('%s - workitem [%s] is created id=%s', jira_project, jira_item, vsts_id)
            else:
                workitem = wit_client.get_work_item(id=vsts_id)
                if html2text(workitem.fields['System.Description']) != html2text(issue_description):
                    logger.info('%s - update work item [%s] with vsts_id=%s, state=%s', jira_project, jira_item,
                                vsts_id,
                                STATES.get(issue.fields.status.name), )
                    workitem = wit_client.update_work_item(id=vsts_id, document=document)
                    logger.info('%s - workitem [%s] is updated vsts_id=%s', jira_project, jira_item, vsts_id)
            # Process comments and attachments
            exists_attachments = []
            try:
                exists_attachments = [rel.attributes.get('name') for rel in workitem.relations if
                                      rel.rel == 'AttachedFile']
            except:
                pass
            for attachment in issue.fields.attachment:
                attachment_filename = attachment.filename
                if attachment_filename in exists_attachments:
                    continue
                logger.info('%s - try to get the attachment [%s] from [%s] attachment_id=%s', jira_project,
                            attachment_filename, jira_item,
                            attachment.id)
                tmpfile = os.path.join(tmpdir, attachment_filename)
                try:
                    os.remove(tmpfile)
                except:
                    pass
                with open(tmpfile, 'wb+') as f:
                    f.write(attachment.get())
                logger.info('%s - the temporary file for [%s] is saved to [%s]', jira_project, jira_item, tmpfile)
                logger.info('%s - try to send the attachment [%s] from [%s] vsts_id=%s', jira_project,
                            attachment_filename, jira_item, vsts_id)
                with open(tmpfile, 'rb') as f:
                    try:
                        # this one bugs, it should pass BufferStream in place of a string
                        # created_attachment = wit_client.create_attachment(upload_stream=f,
                        #                                                   file_name=attachment_filename,
                        #                                                   upload_type='Simple')
                        created_attachment = old_client.upload_attachment(attachment_filename, f)
                    except:
                        if not SKIP_LARGE_ATTACHMENTS:
                            logger.error(traceback.format_exc())
                            raise click.Abort()
                        else:
                            logger.warning('%s - the attachgment [%s] for [%s] is skipped', jira_project,
                                           attachment_filename, jira_item)
                            continue
                logger.info('%s - the attachment [%s] for [%s] is uploaded url=%s', jira_project, attachment_filename,
                            jira_item, created_attachment.url)
                try:
                    os.remove(tmpfile)
                except:
                    pass
                attachment_doc = []
                attachment_doc.append(_create_work_item_field_patch_operation(
                    'add',
                    '/relations/-',
                    {
                        'rel': 'AttachedFile',
                        'url': created_attachment.url,
                        'attributes': {
                            'comment': "Author: {} - Created Date: {}".format(attachment.author, attachment.created)
                        }
                    }
                )
                )
                workitem = wit_client.update_work_item(id=vsts_id, document=attachment_doc)
                logger.info('%s - the  attachment [%s] for [%s] is created id=%s', jira_project, attachment_filename,
                            jira_item, vsts_id)
            _old_author = workitem
            # End comments and attachments
            if move_state:
                if issue.fields.status.name in STATES:
                    idx = 0
                    for project_state in PROJECT_STATES:
                        idx += 1
                        if workitem.fields['System.State'] == project_state:
                            break
                    for project_state in PROJECT_STATES[idx:]:
                        if workitem.fields['System.State'] == STATES[issue.fields.status.name]:
                            break
                        document = [_create_work_item_field_patch_operation('add', 'System.State', project_state)]
                        old_state = workitem.fields['System.State']
                        logger.debug('%s - try to pass the state of [%s] from [%s] to [%s]', jira_project, jira_item,
                                     old_state,
                                     project_state)
                        workitem = wit_client.update_work_item(document=document, id=vsts_id)
                        logger.debug('%s - the state of [%s] is passed from [%s] to [%s]', jira_project, jira_item,
                                     old_state,
                                     workitem.fields['System.State'])
                else:
                    logger.warning('%s - the status [%s] of [%s] is not mapped', jira_project, issue.fields.status.name,
                                   jira_item)
        except:
            logger.error(traceback.format_exc())
            raise click.Abort()
    logger.info('%s - end processing nbr_issues=%s time=%s seconds', jira_project, nbr_issues,
                round(time.time() - start, 2))
    try:
        shutil.rmtree(tmpdir)
    except:
        pass
    LAST_SYNC = LAST_UPDATED if LAST_UPDATED and LAST_SYNC and LAST_UPDATED > LAST_SYNC else LAST_SYNC
    PROJECTS[jira_project]['last_sync'] = LAST_SYNC or LAST_UPDATED
    logger.info('%s - set the last sync to %s', jira_project, LAST_SYNC)
    __update_config_file(config, data)


def _main(ctx, validate, logger, config, issue_to_send):
    """CLI for Jira2Vsts"""
    start = time.time()
    data = __validate_and_get_data(config, logger, validate)
    VSTS_URL = data['vsts']['url']
    url_pattern = re.compile(r"https?://(www\.)?", re.IGNORECASE)
    VSTS_SHORT_URL = url_pattern.sub('', VSTS_URL).strip().strip('/')
    VSTS_TOKEN = data['vsts']['access_token']
    JIRA_URL = data['jira']['url']
    PROJECTS = data['projects']
    JIRA_PROJECTS = [k for k, v in data['projects'].items() if v['active']]
    JIRA_USERNAME = data['jira']['username']
    JIRA_PASSWORD = data['jira']['password']
    STATES = data.get('states', {})
    JIRA_BROWSE = urljoin(JIRA_URL, os.path.normpath(urlparse(JIRA_URL).path) + '/browse/%s')
    try:
        jira = JIRA(JIRA_URL, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))
        logger.info('connection successful to jira')
        if validate:
            click.echo('connection successful to jira')
    except:
        if validate:
            click.echo(traceback.format_exc())
        logger.error(traceback.format_exc())
        raise click.Abort()
    try:
        credentials = BasicAuthentication('', VSTS_TOKEN)
        connection = VssConnection(base_url=VSTS_URL, creds=credentials)
        wit_client = connection.get_client(
            'vsts.work_item_tracking.v4_1.work_item_tracking_client.WorkItemTrackingClient')
        old_client = VstsClient(VSTS_SHORT_URL, data['vsts']['access_token'])
        logger.info('connection successful to vsts')
        if validate:
            click.echo('connection successful to vsts')
    except:
        if validate:
            click.echo(traceback.format_exc())
        logger.error(traceback.format_exc())
        raise click.Abort()
    if validate:
        raise click.Abort()
    # STARTING THE PROCESS
    logger.info('start processing after connecting')
    logger.info('Jira projects to process : %s', JIRA_PROJECTS)
    threads = []
    for jira_project in JIRA_PROJECTS:
        t = threading.Thread(target=__process_project,
                             args=(
                                 logger,
                                 config,
                                 data,
                                 old_client,
                                 wit_client,
                                 jira,
                                 jira_project,
                                 PROJECTS,
                                 STATES,
                                 JIRA_BROWSE,
                                 issue_to_send
                             ))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    logger.info('end processing all projects time=%s seconds', round(time.time() - start, 2))


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
