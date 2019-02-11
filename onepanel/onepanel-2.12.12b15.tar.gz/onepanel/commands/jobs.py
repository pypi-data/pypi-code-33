"""
Job commands
"""
import base64
import glob
import json
import os
import shutil
import stat
import subprocess
import sys
import threading
import logging
from distutils import dir_util

from onepanel.utilities.aws_utility import AWSUtility

import click
import configobj
import websocket

import onepanel.models.models as models
from onepanel.utilities.s3_authenticator import S3Authenticator
from onepanel.models.job import Job
from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from onepanel.commands.projects import ProjectViewController
from onepanel.types.dataset_mount_identifier import DATASET_MOUNT_IDENTIFIER
from onepanel.types.git_source import GIT_SOURCE

COMMON_LOGGER = 'common_logger'


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        if cmd_name == 'ls':
            return click.Group.get_command(self, ctx, 'list')

        return None


class JobViewController(APIViewController):
    JOB_OUTPUT_FILE = os.path.join('.onepanel','output')
    s3_bucket_name = 'onepanel-datasets'

    @staticmethod
    def get_s3_root_for_job_output(account_uid='', project_uid='', job_uid=''):
        return '{account_uid}/projects/{project_uid}/jobs/{job_uid}/output'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid
        )

    @staticmethod
    def get_s3_compressed_file_for_job_output(account_uid='',project_uid='',job_uid=''):
        return '{account_uid}/projects/{project_uid}/jobs/{job_uid}/job-{job_uid}-output.tar.gz'.format(
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid
        )

    def __init__(self, conn):
        APIViewController.__init__(self, conn)
        self.job_uid = None
        self.project_account_uid = None
        self.project_uid = None


    @staticmethod
    def get_credentials_from_current_path():
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            return None

        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        if not os.path.isfile(project_file):
            return None

        cfg = configobj.ConfigObj(project_file)

        project_uid = cfg['uid']
        project_account_uid = cfg['account_uid']

        if len(project_uid) < 1 or len(project_account_uid) < 1:
            return None

        return {
            'project_account_uid': project_account_uid,
            'project_uid': project_uid
        }

    def init_credentials_retrieval(self):
        # Figure out the  account uid and project uid from file
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        if not os.path.isfile(project_file):
            print("ERROR.Project file does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + project_file)
            exit(-1)

        cfg = configobj.ConfigObj(project_file)

        project_uid = cfg['uid']
        project_account_uid = cfg['account_uid']

        if len(project_uid) < 1 or len(project_account_uid) < 1:
            print("ERROR.Project file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.project_account_uid = project_account_uid
        self.project_uid = project_uid

    def init_credentials_job_output(self):
        # Figure out the job uid, account uid and project uid from file
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        job_output_file = os.path.join(home, JobViewController.JOB_OUTPUT_FILE)
        if not os.path.isfile(job_output_file):
            print("ERROR.Job file does not exist, cannot carry out all jobs operations.")
            print("DETAILS." + job_output_file)
            exit(-1)

        cfg = configobj.ConfigObj(job_output_file)

        job_uid = cfg['uid']
        project_uid = cfg['project_uid']
        account_uid = cfg['account_uid']

        if len(job_uid) < 1 or len(project_uid) < 1 or len(account_uid) < 1:
            print("ERROR.Project file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.job_uid = job_uid
        self.project_uid = project_uid
        self.project_account_uid = account_uid

    def init_endpoint(self):
        # Generate the endpoint
        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs'.format(
            root=self.conn.URL,
            account_uid=self.project_account_uid,
            project_uid=self.project_uid
        )

    def create(self, job):
        return self.post(post_object=job, json_encoder=models.APIJSONEncoder)

    def stop(self, account_uid=None, project_uid=None, job_uid=None):
        if account_uid is None and project_uid is None:
            account_uid = self.project_account_uid,
            project_uid = self.project_uid

        endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/job/'.format(
            root=self.conn.URL,
            account_uid=account_uid,
            project_uid=project_uid
        )

        return self.delete_v2(job_uid, '/active', endpoint=endpoint)

    def delete_job(self, account_uid=None, project_uid=None, job_uid=None):
        if account_uid is None and project_uid is None:
            account_uid = self.project_account_uid,
            project_uid = self.project_uid

        endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/job/'.format(
            root=self.conn.URL,
            account_uid=account_uid,
            project_uid=project_uid
        )

        return self.delete_v2(job_uid, endpoint=endpoint)


@click.group(cls=AliasedGroup, help='Job commands group')
@click.pass_context
def jobs(ctx):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    project_vc = ProjectViewController(ctx.obj['connection'])
    path = os.getcwd()
    if project_vc.exists_local(path):
        project_vc.from_directory(path)
        ctx.obj['project'] = project_vc
    else:
        # Return error before reaching other CLI commands:
        print('This project is not initialized, type "onepanel init" to initialize this project')
        sys.exit(1)


@jobs.command('create', help='Execute a command on a remote machine in the current project')
@click.argument(
    'command',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type ID. Call "onepanel machine-types list" for IDs.'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Instance template ID. Call "onepanel environments list" for IDs.'
)
@click.option(
    '-s', '--storage',
    type=str,
    required=True,
    help='Storage type ID.'
)
@click.option(
    '-g', '--source_control',
    type=GIT_SOURCE,
    required=False,
    help='''Source control to use. 

            Format: branch_name/commit_hash

            If omitted, latest commit from master is used.
         '''
)
@click.option(
    '-d', '--mount',
    type=DATASET_MOUNT_IDENTIFIER,
    required=False,
    multiple=True,
    help='''Datasets to mount. 

            Format: source=account_name/dataset_name,version=version_of_dataset,destination=folder_to_call_it

            Example: source=onepaneldemo/images,version=3,destination=cats

            The version is optional. If omitted, it'll use the latest version.

            The destination is optional. If omitted, it'll use account_name/dataset_name/version
        '''
)
@click.pass_context
@login_required
def create_job(ctx, command, machine_type, environment, storage, mount, source_control):
    job = Job()
    job.command = command
    job.machine_type.uid = machine_type
    job.instance_template.uid = environment
    job.volume_type.uid = storage
    job.datasetMountIdentifiers = mount
    job.gitSource = source_control

    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    response = vc.create(job)

    if response['status_code'] == 200:
        print('New job created: {}'.format(response['data']['uid']))
    else:
        print("An error occurred: {}".format(response['data']))


@jobs.command('list', help='Show commands executed on remote machines')
@click.option(
    '-a', '--all',
    type=bool,
    is_flag=True,
    default=False,
    help='Include finished commands'
)
@click.pass_context
@login_required
def list_jobs(ctx, all):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    items = vc.list(params='?running=true' if not all else '')

    if items is None or len(items) == 0:
        print('No jobs found. Use "--all" flag to retrieve completed jobs.')
        return

    items = [Job.from_json(item).simple_view() for item in items]

    vc.print_items(items, fields=['uid', 'state', 'command'], field_names=['ID', 'STATE', 'COMMAND'])


@jobs.command('stop', help='Stop a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def kill_job(ctx, job_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    ctx.obj['vc'].delete(job_uid, field_path='/active', message_on_success='Job stopped',
                         message_on_failure='Job not found')


@jobs.command('logs', help='Show a log of the command')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def job_logs(ctx, job_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    project = ctx.obj['project']

    job_data = vc.get('/' + job_uid, field_path='/logs')

    if job_data['status_code'] != 400:
        if job_data['data'] is None:
            print('Job not found.')
            return
        log = job_data['data']
        print(log)
    else:
        # Streaming via WebSocket
        # See https://pypi.python.org/pypi/websocket-client/

        def on_message(ws, message):
            if message[0] == '0':
                message = base64.b64decode(message[1:]).decode('utf-8', 'ignore')
                sys.stdout.write(message)
                sys.stdout.flush()

        def on_error(ws, error):
            if isinstance(error, websocket.WebSocketConnectionClosedException):
                return

            if isinstance(error, KeyboardInterrupt):
                return

            if error.status_code == 502 or error.status_code == 503:
                print('Job {} is preparing'.format(job_uid))
            else:
                print(error)

        def on_close(ws):
            print('connection closed')

        def on_open(ws):
            def send_auth_token(*args):
                ws.send(json.dumps({'Authtoken': ''}))

            threading.Thread(target=send_auth_token).start()

        ws_url = '{ws_root}/{account_uid}/projects/{project_uid}/jobs/{job_uid}/logs/ws?id_token={token}'.format(
            ws_root='wss://c.onepanel.io',
            account_uid=project.account_uid,
            project_uid=project.project_uid,
            job_uid=job_uid,
            token=ctx.obj['connection'].token
        )

        ws = websocket.WebSocketApp(
            url=ws_url,
            on_message=on_message,
            on_open=on_open,
            on_error=on_error
        )

        ws.run_forever()

    return False


def jobs_download_output(ctx, path, directory,archive_flag):
    jvc = JobViewController(ctx.obj['connection'])
    #
    # Resource
    #
    dirs = path.split('/')
    git_utility = ctx.obj['git_utility']

    # Job output: Method 2
    # <account_uid>/projects/<project_uid>/jobs/<job_uid>
    if len(dirs) == 5:
        try:
            account_uid, projects_dir, project_uid, jobs_dir, job_uid = dirs
            assert (projects_dir == 'projects') and (jobs_dir == 'jobs')
        except:
            print('Incorrect job path')
            return None
    else:
        print('Incorrect job uid')
        return None

    #
    # Directory
    #
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # Check how the job output is stored
    jvc.project_account_uid = account_uid
    jvc.project_uid = project_uid
    jvc.init_endpoint()
    job_data = jvc.get('/' + job_uid)
    if job_data['data'] is None:
        print("Job not found.")
        return False
    is_legacy = job_data['data']['isLegacy']
    if is_legacy:
        if archive_flag is True:
            print("--archive is not supported for this job output.")
        else:
            #
            # Clone
            #
            onepanel_download_path = '.onepanel_download'
            if os.path.isdir(onepanel_download_path):
                shutil.rmtree(onepanel_download_path,
                              onerror=remove_readonly)  # Cleaning after previous errors to avoid "is not an empty directory" error
            cmd = (
                    git_utility.get_git_clone_str() + ' -b job-{job_uid} https://{user_uid}:{gitlab_token}@{host}/{account_uid}/{project_uid}-output.git '
                                                      '.onepanel_download'
            ).format(
                host=os.getenv('GITLAB_GIT_HOST', 'git.onepanel.io'),
                user_uid=ctx.obj['connection'].user_uid,
                gitlab_token=ctx.obj['connection'].gitlab_impersonation_token,
                account_uid=account_uid,
                project_uid=project_uid,
                job_uid=job_uid,
                dir=home
            )
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            p.wait()
            status_code = p.returncode
            if status_code == 128:
                print("Could not find the remote git repository.")
                exit(0)

            jobs_path = '/jobs/{job_uid}/output/'.format(job_uid=job_uid)
            copy_from_dir = onepanel_download_path + jobs_path
            if not os.path.exists(copy_from_dir):
                print("This job did not create any output or output was not saved. \n" +
                      "If you want to save and version control your output, modify your script to "
                      "save all output to the '/onepanel/output' directory.\n")
                if os.path.isdir(onepanel_download_path):
                    shutil.rmtree(onepanel_download_path,
                                  onerror=remove_readonly)
                exit(0)
            else:
                dir_util.copy_tree(copy_from_dir, home)

            if os.path.isdir(onepanel_download_path):
                shutil.rmtree(onepanel_download_path, onerror=remove_readonly)

            if p.returncode == 0:
                print('Job output downloaded to: {dir}'.format(dir=home))
                return True
            else:
                print('Unable to download')
                return False
    else:
        s3auth = S3Authenticator(ctx.obj['connection'])
        creds = s3auth.get_s3_credentials(jvc.project_account_uid, 'projects', jvc.project_uid)
        if creds['data'] is None:
            print("Unable to get S3 credentials. Exiting.")
            return False
        aws_access_key_id = creds['data']['AccessKeyID']
        aws_secret_access_key = creds['data']['SecretAccessKey']
        aws_session_token = creds['data']['SessionToken']
        aws_util = AWSUtility(aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
        s3_download_to_path = home
        if archive_flag is True:
            print("Attempting to download the compressed output file to {home} directory.".format(home=s3_download_to_path))
            s3_path_to_download_from = jvc.get_s3_compressed_file_for_job_output(account_uid, project_uid, job_uid)
            full_path = 's3://{bucket}/{path}'.format(bucket=aws_util.get_dataset_bucket_name(),
                                                      path=s3_path_to_download_from)
            investigation_results = aws_util.check_s3_path_for_files(full_path,False)
            if investigation_results['code'] == -1:
                print("Error encountered.")
                print(investigation_results['msg'])
                return
            if investigation_results['code'] == 0 and investigation_results['data'] == 0:
                print("This job did not create any output or output was not saved. \n" +
                      "If you want to save and version control your output, modify your script to "
                      "save all output to the '/onepanel/output' directory.\n")
                return
            exit_code = aws_util.download(s3_download_to_path,s3_path_to_download_from)
            if exit_code != 0:
                print("Error encountered.")
                return
        else:
            print("Attempting to download output to {home} directory.".format(home=s3_download_to_path))
            s3_path_to_download_from = jvc.get_s3_root_for_job_output(account_uid, project_uid, job_uid)
            full_path = 's3://{bucket}/{path}'.format(bucket=aws_util.get_dataset_bucket_name(),path=s3_path_to_download_from)
            investigation_results = aws_util.check_s3_path_for_files(full_path)
            if investigation_results['code'] == -1:
                print("Error encountered.")
                print(investigation_results['msg'])
                return
            if investigation_results['code'] == 0 and investigation_results['data'] == 0:
                print("This job did not create any output or output was not saved. \n" +
                    "If you want to save and version control your output, modify your script to "
                    "save all output to the '/onepanel/output' directory.\n")
                return
            # Check if there any actual files to download from the output
            exit_code = aws_util.download_all(s3_download_to_path,s3_path_to_download_from)
            if exit_code != 0:
                print("Error encountered.")
                return
        print("Finished downloading.")



@jobs.command('delete', help='Delete a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def delete_job(ctx, job_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    ctx.obj['vc'].delete(job_uid, message_on_success='Job deleted', message_on_failure='Job not found')

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def upload_output(ctx,suppress_output=False):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.init_credentials_job_output()

    files = glob.glob("*")
    if len(files) < 1:
        click.echo("Cannot find any files in current dir, exiting.")
        return

    # Authenticate for S3
    s3auth = S3Authenticator(ctx.obj['connection'])
    creds = s3auth.get_s3_credentials(vc.project_account_uid, 'projects', vc.project_uid)
    if creds['data'] is None:
        print("Unable to get S3 credentials. Exiting.")
        return False
    aws_access_key_id = creds['data']['AccessKeyID']
    aws_secret_access_key = creds['data']['SecretAccessKey']
    aws_session_token = creds['data']['SessionToken']

    job_source_dir = os.curdir
    s3_push_to_dir = '{account_uid}/projects/{project_uid}/jobs/{job_uid}'.format(
        account_uid=vc.project_account_uid,
        project_uid=vc.project_uid,
        job_uid=vc.job_uid
    )

    aws_util = AWSUtility(aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          aws_session_token=aws_session_token)
    aws_util.suppress_output = suppress_output

    exit_code = aws_util.upload_dir(job_source_dir, s3_push_to_dir, '.onepanel/*')
    if exit_code != 0:
        click.echo('\nError with pushing up files.')
        return

# This is similar to the function above, and the two need to be merged. 
def upload_output_with_parameters(ctx, job_uid, project_uid, project_account_uid, suppress_output=False, source_directory=None, destination=None):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.job_uid = job_uid
    vc.project_uid = project_uid
    vc.project_account_uid = project_account_uid

    logging.getLogger(COMMON_LOGGER).info("Arguments: {}, {}, {}".format(job_uid, project_uid, project_account_uid))

    files = glob.glob("*")
    if len(files) < 1:
        logging.getLogger(COMMON_LOGGER).info("Cannot find any files in current dir, exiting.")
        click.echo("Cannot find any files in current dir, exiting.")
        return

    # Authenticate for S3
    s3auth = S3Authenticator(ctx.obj['connection'])

    creds = s3auth.get_s3_credentials(vc.project_account_uid, 'projects', vc.project_uid)
    if creds['data'] is None:
        logging.getLogger(COMMON_LOGGER).warning("Unable to get S3 credentials. Exiting. {} {}".format(vc.project_account_uid, vc.project_uid))
        print("Unable to get S3 credentials. Exiting.")
        return False
    aws_access_key_id = creds['data']['AccessKeyID']
    aws_secret_access_key = creds['data']['SecretAccessKey']
    aws_session_token = creds['data']['SessionToken']

    job_source_dir = os.curdir
    if source_directory is not None:
        job_source_dir = source_directory

    s3_push_to_dir = '{account_uid}/projects/{project_uid}/jobs/{job_uid}'.format(
        account_uid=vc.project_account_uid,
        project_uid=vc.project_uid,
        job_uid=vc.job_uid
    )

    if destination is not None:
        s3_push_to_dir = destination

    aws_util = AWSUtility(aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          aws_session_token=aws_session_token)
    aws_util.suppress_output = suppress_output

    exit_code = aws_util.upload_dir(job_source_dir, s3_push_to_dir, '.onepanel/*')
    if exit_code != 0:
        logging.getLogger(COMMON_LOGGER).warning('\nError with pushing up files.')
        click.echo('\nError with pushing up files.')
        return

    logging.getLogger(COMMON_LOGGER).info("Finished output upload.")
    print("Finished output upload.")