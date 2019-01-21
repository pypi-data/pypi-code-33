# -*- coding: utf8 -*-
import click

from missinglink.commands.commons import output_result
from missinglink.commands.utils import monitor_logs
from .utilities.job_parser import JobParser, job_params
from .utilities.options import CommonOptions


@click.group('run', help='runs an experiment on a cluster. By defaults run on a local cluster ')
def run_commands():
    pass


@run_commands.command('track')
@click.pass_context
@CommonOptions.org_option(required=False)
def run_experiment(ctx, **kwargs):
    jp = JobParser(ctx, **kwargs)
    print(jp.build_src_pointer({}))


@run_commands.command('xp')
@click.pass_context
@job_params
def run_experiment(ctx, **kwargs):
    jp = JobParser(ctx, **kwargs)

    job_env = jp.prepare_job_context()
    if job_env is None:
        # Save recipe
        return

    jp.prepare_encrypted_data(job_env.org, job_env.input_data, job_env.docker_creds, job_env.secure_env)
    result = jp.submit_job(job_env)
    output_result(ctx, result, ['ok', 'job'])

    _attach(job_env.attach, ctx, job_env.org, result['job'], job_env.disable_colors)


def _attach(attach, ctx, org, job_id, disable_colors):
    if attach:
        url = '{org}/run/{job_id}/logs'.format(org=org, job_id=job_id)
        monitor_logs(ctx, url, disable_colors)


@run_commands.command('logs')
@CommonOptions.org_option()
@click.option('--job', type=str)
@click.option('--disable-colors', is_flag=True, required=False)
@click.pass_context
def job_logs(ctx, org, job, disable_colors):
    url = '{org}/run/{job}/logs'.format(org=org, job=job)
    monitor_logs(ctx, url, disable_colors)


def _attach_in_bg(attach, ctx, org, job_id, disable_colors):
    import threading
    thread = threading.Thread(target=_attach, args=(attach, ctx, org, job_id, disable_colors))
    thread.daemon = True
    thread.start()


@run_commands.command('local')
@click.pass_context
@click.option('--link-aws/--no-aws-link', required=False, default=True)
@click.option('--env-aws/--no-aws-env', required=False, default=True)
@click.option('--link-gcp/--no-gcp', required=False, default=True)
@click.option('--link-azure/--no-azure', required=False, default=True)
@job_params
def local(ctx, **kwargs):
    jp = JobParser(ctx, **kwargs)
    jp.validate_no_running_containers()
    jp.docker_tools.pull_rm_image()
    job_env = jp.prepare_job_context()
    if job_env is None:
        # Save recipe
        return

    job_id, docker_command_params = jp.build_local_command(job_env)
    click.echo('Starting Resource Manager for job: %s' % job_id)

    res = jp.run_docker(docker_command_params)
    _attach_in_bg(True, ctx, job_env.org, job_id, job_env.disable_colors)
    for x in res.logs(stream=True, stderr=True, stdout=True):
        click.echo(x.strip())
