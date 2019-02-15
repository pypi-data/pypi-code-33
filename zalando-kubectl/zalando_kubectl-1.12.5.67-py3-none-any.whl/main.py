import atexit
import base64
import hashlib
import os
import random
import string
import subprocess
import sys
import time
import uuid
from itertools import chain
from pathlib import Path
import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc
import humanize

import click
import clickclick
import requests
import stups_cli
import stups_cli.config
import zalando_kubectl
import zalando_kubectl.access_request as access_request
import zalando_kubectl.traffic
import zalando_kubectl.registry as registry
import zalando_kubectl.secrets
from zalando_kubectl.models.deployment import Deployment, DeploymentUpdateError
from zalando_kubectl.models.stack import StackUpdateError
from zalando_kubectl.utils import auth_headers, get_api_server_url, current_user
from clickclick import Action, info, print_table, AliasedGroup

from . import kube_config
from .templating import (read_senza_variables, prepare_variables,
                         copy_template)

APP_NAME = 'zalando-kubectl'
KUBECTL_URL_TEMPLATE = 'https://storage.googleapis.com/kubernetes-release/release/{version}/bin/{os}/{arch}/kubectl'
KUBECTL_VERSION = 'v1.12.5'
KUBECTL_SHA256 = {
    'linux': 'f52abcfbcb74f590a2229364afee11271ce597add3eeceefc1dc174590e2dff8',
    'darwin': '17f461c0109a9d288d975fdfea89258b3a8ea6b6154ef2aa8d5ebcf8e9e29371'
}

STERN_URL_TEMPLATE = 'https://github.com/wercker/stern/releases/download/{version}/stern_{os}_{arch}'
STERN_VERSION = '1.10.0'
STERN_SHA256 = {
    'linux': 'a0335b298f6a7922c35804bffb32a68508077b2f35aaef44d9eb116f36bc7eda',
    'darwin': 'b91dbcfd3bbda69cd7a7abd80a225ce5f6bb9d6255b7db192de84e80e4e547b7'
}
UPDATE_BLOCK_CONFIG_ITEM = 'cluster_update_block'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

STYLES = {
    'REQUESTED': {'fg': 'yellow', 'bold': True},
    'APPROVED': {'fg': 'green'},
}
MAX_COLUMN_WIDTHS = {
    'reason': 50,
}


def load_config():
    return stups_cli.config.load_config(APP_NAME)


def store_config(config):
    stups_cli.config.store_config(config, APP_NAME)


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def click_cli(ctx):
    ctx.obj = load_config()


def ensure_binary(name, url_template, version, sha256):
    path = Path(os.getenv('KUBECTL_DOWNLOAD_DIR') or click.get_app_dir(APP_NAME))
    binary = path / '{}-{}'.format(name, version)

    if not binary.exists():
        try:
            binary.parent.mkdir(parents=True)
        except FileExistsError:
            # support Python 3.4
            # "exist_ok" was introduced with 3.5
            pass

        platform = sys.platform  # linux or darwin
        arch = 'amd64'  # FIXME: hardcoded value
        url = url_template.format(version=version, os=platform, arch=arch)
        with Action('Downloading {} to {}..'.format(url, binary)) as act:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            # add random suffix to allow multiple downloads in parallel
            random_suffix = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            local_file = binary.with_name('{}.download-{}'.format(binary.name, random_suffix))
            m = hashlib.sha256()
            with local_file.open('wb') as fd:
                for i, chunk in enumerate(response.iter_content(chunk_size=4096)):
                    if chunk:  # filter out keep-alive new chunks
                        fd.write(chunk)
                        m.update(chunk)
                        if i % 256 == 0:  # every 1MB
                            act.progress()
            if m.hexdigest() != sha256[platform]:
                act.fatal_error('CHECKSUM MISMATCH')
            local_file.chmod(0o755)
            local_file.rename(binary)

    return str(binary)


def ensure_kubectl():
    return ensure_binary('kubectl', KUBECTL_URL_TEMPLATE, KUBECTL_VERSION, KUBECTL_SHA256)


def ensure_stern():
    return ensure_binary('stern', STERN_URL_TEMPLATE, STERN_VERSION, STERN_SHA256)


def get_registry_url(config):
    try:
        return config['cluster_registry'].rstrip('/')
    except KeyError:
        raise Exception("Cluster registry URL missing, please reconfigure zkubectl")


def fix_url(url):
    # strip potential whitespace from prompt
    url = url.strip()
    if url and not url.startswith('http'):
        # user convenience
        url = 'https://' + url
    return url


def proxy(args=None):
    kubectl = ensure_kubectl()

    if not args:
        args = sys.argv[1:]

    sys.exit(subprocess.call([kubectl] + args))


@click_cli.command('completion', context_settings={'help_option_names': [], 'ignore_unknown_options': True})
@click.argument('kubectl-arg', nargs=-1, type=click.UNPROCESSED)
def completion(kubectl_arg):
    '''Output shell completion code for the specified shell'''
    kubectl = ensure_kubectl()
    cmdline = [kubectl, 'completion']
    cmdline.extend(kubectl_arg)
    popen = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    for stdout_line in popen.stdout:
        print(stdout_line.decode('utf-8').replace('kubectl', 'zkubectl'), end='')
    popen.stdout.close()


def looks_like_url(alias_or_url: str):
    if alias_or_url.startswith('http:') or alias_or_url.startswith('https:'):
        # https://something
        return True
    elif len(alias_or_url.split('.')) > 2:
        # foo.example.org
        return True
    return False


def configure_zdeploy(cluster):
    try:
        import zalando_deploy_cli.api
        zalando_deploy_cli.api.configure_for_cluster(cluster)
    except ImportError:
        pass


def login(config, cluster_or_url: str):
    if not cluster_or_url:
        cluster_or_url = click.prompt('Cluster ID or URL of Kubernetes API server')

    alias = None

    if looks_like_url(cluster_or_url):
        url = fix_url(cluster_or_url)
    else:
        cluster = registry.get_cluster_by_id_or_alias(get_registry_url(config), cluster_or_url)
        url = cluster['api_server_url']
        alias = cluster['alias']
        configure_zdeploy(cluster)

    config['api_server'] = url
    store_config(config)
    return url, alias


@click_cli.command('configure')
@click.option('--cluster-registry', required=True, help="Cluster registry URL")
@click.pass_obj
def configure(config, cluster_registry):
    '''Set the Cluster Registry URL'''
    config['cluster_registry'] = cluster_registry
    store_config(config)


def _open_dashboard_in_browser():
    import webbrowser
    # sleep some time to make sure "kubectl proxy" runs
    url = 'http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/'
    url += '#!/workload?namespace=' + kube_config.get_current_namespace()
    with Action('Waiting for local kubectl proxy..') as act:
        for i in range(20):
            time.sleep(0.1)
            try:
                requests.get(url, timeout=2)
            except Exception:
                act.progress()
            else:
                break
    info('\nOpening {} ..'.format(url))
    webbrowser.open(url)


@click_cli.command('dashboard')
@click.pass_obj
def dashboard(config):
    '''Open the Kubernetes dashboard UI in the browser'''
    import threading
    # first make sure kubectl was downloaded
    ensure_kubectl()
    thread = threading.Thread(target=_open_dashboard_in_browser)
    # start short-lived background thread to allow running "kubectl proxy" in main thread
    thread.start()
    kube_config.update_token()
    proxy(['proxy'])


def _open_kube_ops_view_in_browser():
    import webbrowser
    # sleep some time to make sure "kubectl proxy" and kube-ops-view run
    url = 'http://localhost:8080/'
    with Action('Waiting for Kubernetes Operational View..') as act:
        while True:
            time.sleep(0.1)
            try:
                requests.get(url, timeout=2)
            except Exception:
                act.progress()
            else:
                break
    info('\nOpening {} ..'.format(url))
    webbrowser.open(url)


@click_cli.command('opsview')
@click.pass_obj
def opsview(config):
    '''Open the Kubernetes Operational View (kube-ops-view) in the browser'''
    import threading
    # first make sure kubectl was downloaded
    ensure_kubectl()

    # pre-pull the kube-ops-view image
    image_name = 'hjacobs/kube-ops-view:0.7.1'
    subprocess.check_call(['docker', 'pull', image_name])

    thread = threading.Thread(target=_open_kube_ops_view_in_browser, daemon=True)
    # start short-lived background thread to allow running "kubectl proxy" in main thread
    thread.start()
    if sys.platform == 'darwin':
        # Docker for Mac: needs to be slightly different in order to navigate the VM/container inception
        opts = ['-p', '8080:8080', '-e', 'CLUSTERS=http://docker.for.mac.localhost:8001']
    else:
        opts = ['--net=host']
    subprocess.Popen(['docker', 'run', '--rm', '-i'] + opts + [image_name])
    kube_config.update_token()
    proxy(['proxy', '--accept-hosts=.*'])


@click_cli.command('logtail', context_settings=dict(
    ignore_unknown_options=True,
    help_option_names=[],
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def logtail(args):
    '''Tail multiple pods and containers'''
    stern = ensure_stern()
    kube_config.update_token()
    sys.exit(subprocess.call([stern] + list(args)))


def do_list_clusters(config):
    cluster_registry = get_registry_url(config)

    response = requests.get('{}/kubernetes-clusters'.format(cluster_registry),
                            params={'lifecycle_status': 'ready', 'verbose': 'false'},
                            headers=auth_headers(), timeout=20)
    response.raise_for_status()
    data = response.json()
    rows = []
    for cluster in data['items']:
        status = cluster.get('status', {})
        version = status.get('current_version', '')[:7]
        if status.get('next_version') and status.get('current_version') != status.get('next_version'):
            version += ' (updating)'
        cluster['version'] = version
        rows.append(cluster)
    rows.sort(key=lambda c: (c['alias'], c['id']))
    print_table('id alias environment channel version'.split(), rows)
    return rows


@click_cli.command('list-clusters')
@click.pass_obj
def list_clusters(config):
    '''List all Kubernetes cluster in "ready" state'''
    do_list_clusters(config)


@click_cli.command('list')
@click.pass_context
def list_clusters_short(ctx):
    '''Shortcut for "list-clusters"'''
    ctx.forward(list_clusters)


@click_cli.command('login')
@click.argument('cluster', required=False)
@click.pass_obj
def do_login(config, cluster):
    '''Login to a specific cluster'''
    url, alias = login(config, cluster)
    with Action('Writing kubeconfig for {}..'.format(url)):
        kube_config.update(url, alias)


@click_cli.command('encrypt')
@click.option('--cluster', help='Cluster ID or alias')
@click.option('--strip/--no-strip', default=True, help='Remove the trailing newline from the data, enabled by default')
@click.option('--kms-keyid', help='KMS key ID')
@click.pass_obj
def encrypt(config, cluster, kms_keyid, strip):
    """Encrypt a value for use in a deployment configuration"""
    registry_url = get_registry_url(config)
    if cluster:
        cluster_metadata = registry.get_cluster_by_id_or_alias(registry_url, cluster)
    else:
        cluster_metadata = registry.get_cluster_with_params(registry_url, api_server_url=get_api_server_url(config))

    if not kms_keyid:
        local_id = cluster_metadata['id'].split(':')[-1]
        kms_keyid = 'alias/{}-deployment-secret'.format(local_id)

    if click.get_text_stream('stdin').isatty():
        plain_text = click.prompt("Data to encrypt", hide_input=True).encode()
    else:
        plain_text = sys.stdin.buffer.read()

    if strip:
        plain_text = plain_text.rstrip(b'\r\n')

    encrypted = zalando_kubectl.secrets.encrypt(cluster_metadata, kms_keyid, plain_text)
    print(encrypted)


@click_cli.command('decrypt')
@click.argument('encrypted_value', required=True)
@click.pass_obj
def decrypt(config, encrypted_value):
    """Decrypt a value encrypted with zkubectl encrypt"""
    registry_url = get_registry_url(config)

    parts = encrypted_value.split(':')
    if parts[0] != 'deployment-secret':
        raise ValueError("Invalid secret format")

    if len(parts) == 3:
        # deployment-secret:cluster:data
        _, alias, data = parts
    elif len(parts) == 4:
        # deployment-secret:version:cluster:data
        _, version, alias, data = parts
        if version != "2":
            raise ValueError("Unsupported secret version {}".format(version))
    else:
        raise ValueError("Invalid secret format")

    cluster_metadata = registry.get_cluster_with_params(registry_url, alias=alias)

    decrypted = zalando_kubectl.secrets.decrypt(cluster_metadata, base64.b64decode(data))
    sys.stdout.buffer.write(decrypted)


def _validate_weight(_ctx, _param, value):
    if value is None:
        return None
    elif not 0.0 <= value <= 100.0:
        raise click.BadParameter("Weight must be between 0 and 100")
    else:
        return value


@click_cli.command('traffic', help='''Print or update backend traffic weights of an ingress.''')
@click.option('--namespace', '-n', help='If present, the namespace scope for this CLI request', required=False)
@click.option('--force', '-f', help='Flag to force the traffic change without waiting for the stackset controller',
              default=False, is_flag=True)
@click.argument('ingress', required=True)
@click.argument('backend', required=False)
@click.argument('weight', required=False, type=float, callback=_validate_weight)
@click.pass_obj
def traffic(config, namespace, force, ingress, backend, weight):
    kube_config.update_token()
    kubectl = ensure_kubectl()

    try:
        if backend is None:
            # print existing weights
            ingress = zalando_kubectl.traffic.get_ingress(kubectl, namespace, ingress)
            zalando_kubectl.traffic.print_weights_table(ingress)
        elif weight is None:
            raise click.UsageError("You must specify the new weight")
        else:
            # update weight for a backend
            ingress = zalando_kubectl.traffic.get_ingress(kubectl, namespace, ingress)
            ingress.set_weight(backend, weight, force)
            zalando_kubectl.traffic.set_ingress_weights(kubectl, namespace, ingress, force)
            zalando_kubectl.traffic.print_weights_table(ingress)
    except subprocess.CalledProcessError as e:
        click_exc = click.ClickException(e.stderr.decode("utf-8"))
        click_exc.exit_code = e.returncode
        raise click_exc


@click_cli.group(name='cluster-update', cls=AliasedGroup, context_settings=CONTEXT_SETTINGS,
                 help='Cluster update related commands')
def cluster_update():
    pass


@cluster_update.command('status')
@click.pass_obj
def cluster_update_status(config):
    """Show the cluster update status"""
    registry_url = get_registry_url(config)
    api_server_url = get_api_server_url(config)
    cluster_metadata = registry.get_cluster_with_params(registry_url, verbose=True, api_server_url=api_server_url)
    alias = cluster_metadata['alias']

    update_block_reason = cluster_metadata.get('config_items', {}).get(UPDATE_BLOCK_CONFIG_ITEM)
    if update_block_reason is not None:
        clickclick.warning("Cluster updates for {} are blocked: {}".format(alias, update_block_reason))
    else:
        status = cluster_metadata.get('status', {})
        current_version = status.get('current_version')
        next_version = status.get('next_version')

        if next_version and next_version != current_version:
            clickclick.warning("Cluster {} is being updated".format(alias))
        else:
            print("Cluster {} is up-to-date".format(alias))


@cluster_update.command('block')
@click.pass_obj
def block_cluster_update(config):
    """Block the cluster from updating"""
    registry_url = get_registry_url(config)
    api_server_url = get_api_server_url(config)
    cluster_metadata = registry.get_cluster_with_params(registry_url, verbose=True, api_server_url=api_server_url)
    alias = cluster_metadata['alias']

    current_reason = cluster_metadata.get('config_items', {}).get(UPDATE_BLOCK_CONFIG_ITEM)
    if current_reason is not None:
        if not click.confirm("Cluster updates already blocked: {}. Overwrite?".format(current_reason)):
            return

    reason = click.prompt("Blocking cluster updates for {}, reason".format(alias))
    reason = "{} ({})".format(reason, current_user())

    registry.update_config_item(registry_url, cluster_metadata['id'], UPDATE_BLOCK_CONFIG_ITEM, reason)
    print("Cluster updates blocked")


@cluster_update.command('unblock')
@click.pass_obj
def unblock_cluster_update(config):
    """Allow updating the cluster"""
    registry_url = get_registry_url(config)
    api_server_url = get_api_server_url(config)
    cluster_metadata = registry.get_cluster_with_params(registry_url, verbose=True, api_server_url=api_server_url)
    alias = cluster_metadata['alias']

    current_reason = cluster_metadata.get('config_items', {}).get(UPDATE_BLOCK_CONFIG_ITEM)
    if current_reason is not None:
        if click.confirm("Cluster update for {} was blocked: {}. Unblock?".format(alias, current_reason)):
            registry.delete_config_item(registry_url, cluster_metadata['id'], UPDATE_BLOCK_CONFIG_ITEM)
            print("Cluster updates unblocked")
    else:
        print("Cluster updates aren't blocked")


def print_help(ctx):
    click.secho('Zalando Kubectl {}\n'.format(zalando_kubectl.__version__), bold=True)

    formatter = ctx.make_formatter()
    click_cli.format_commands(ctx, formatter)
    print(formatter.getvalue().rstrip('\n'))

    click.echo("")
    click.echo("All other commands are forwarded to kubectl:\n")
    proxy(args=["--help"])


@click_cli.command('help')
@click.pass_context
def show_help(ctx):
    '''Show the help message and exit'''
    print_help(ctx)
    sys.exit(0)


@click_cli.command('init')
@click.argument('directory', nargs=-1)
@click.option('-t', '--template',
              help='Use a custom template (default: webapp)',
              metavar='TEMPLATE_ID', default='webapp')
@click.option('--from-senza', help='Convert Senza definition',
              type=click.File('r'), metavar='SENZA_FILE')
@click.option('--kubernetes-cluster')
@click.pass_obj
def init(config, directory, template, from_senza, kubernetes_cluster):
    '''Initializes a new deploy folder with default Kubernetes manifests and
    CDP configuration.

    You can choose a different template using the '-t' option and specifying
    one of the following templates:

    webapp  - Default template with a simple public facing web application
              configured with rolling updates through CDP;

    traffic - Public facing web application configured for blue/green
              deployments, enabling traffic switching;

    senza   - Used for migrating a Senza definition file. You can use
              --from-senza directly instead.
    '''
    if directory:
        path = Path(directory[0])
    else:
        path = Path('.')

    if from_senza:
        variables = read_senza_variables(from_senza)
        template = 'senza'
    else:
        variables = {}

    if kubernetes_cluster:
        cluster_id = kubernetes_cluster
    else:
        info('Please select your target Kubernetes cluster')
        clusters = do_list_clusters(config)
        valid_cluster_names = list(chain.from_iterable((c['id'], c['alias'])
                                                       for c
                                                       in clusters))
        cluster_id = ''
        while cluster_id not in valid_cluster_names:
            cluster_id = click.prompt('Kubernetes Cluster ID to use')

    variables['cluster_id'] = cluster_id

    template_path = Path(__file__).parent / 'templates' / template
    variables = prepare_variables(variables)
    copy_template(template_path, path, variables)

    print()

    notes = path / 'NOTES.txt'
    with notes.open() as fd:
        print(fd.read())


def access_request_username(explicit_user):
    return explicit_user or current_user() or click.prompt("User that should receive access")


@click_cli.group(name='cluster-access', cls=AliasedGroup, context_settings=CONTEXT_SETTINGS,
                 help='Manual/emergency access related commands')
def cluster_access():
    pass


@cluster_access.command('request')
@click.option('--emergency', is_flag=True, help='Request emergency access to the cluster')
@click.option("-i", "--incident",
              help="Incident number, required with --emergency", type=int)
@click.option("-u", "--user",
              help="User that should be given access, defaults to the current user", required=False)
@click.argument("reason", nargs=-1, required=True)
@click.pass_obj
def request_cluster_access(config, emergency, incident, user, reason):
    '''Request access to the cluster'''
    if emergency:
        if not incident:
            raise click.UsageError("You must specify an incident ticket [--incident] when requesting emergency access")
        make_emergency_access_request(config, incident, user, reason)
    else:
        make_manual_access_request(config, user, reason)


@click_cli.command('emergency-access')
@click.option("-i", "--incident",
              help="Incident number", required=True, type=int)
@click.option("-u", "--user",
              help="User that should be given access, defaults to the current user", required=False)
@click.argument("reason", nargs=-1, required=True)
@click.pass_context
def request_emergency_access(ctx, incident, user, reason):
    '''
    DEPRECATED - please use 'cluster-access'.

    DEPRECATED in favor of 'zkubectl cluster-access request --emergency'

    Request 24x7 access to the cluster
    '''
    clickclick.warning("DEPRECATED in favor of 'zkubectl cluster-access request --emergency'")
    ctx.invoke(request_cluster_access, emergency=True, incident=incident, user=user, reason=reason)


def make_emergency_access_request(config, incident, user, reason):
    user = access_request_username(user)
    reference_url = "https://techjira.zalando.net/browse/INC-{}".format(incident) if incident else None
    access_request.create(config, "emergency", reference_url, user, ' '.join(reason))
    click.echo("Emergency access provisioned for {}. Note that it might take a while "
               "before the new permissions are applied.".format(user))


@click_cli.command('manual-access')
@click.argument("reason", nargs=-1, required=True)
@click.pass_context
def request_manual_access(ctx, reason):
    '''
    DEPRECATED - please use 'cluster-access'.

    DEPRECATED in favor of 'zkubectl cluster-access request'

    Request manual access to the cluster'''
    clickclick.warning("DEPRECATED in favor of 'zkubectl cluster-access request'")
    ctx.invoke(request_cluster_access, emergency=False, incident=None, user=None, reason=reason)


def make_manual_access_request(config, user_option, reason):
    user = access_request_username(user_option)
    access_request.create(config, "manual", None, user, ' '.join(reason))
    click.echo("Requested manual access for {}.".format(user))
    click.echo("You can ask your colleague to approve it using these commands:\n")
    current_cluster = kube_config.get_current_context()
    if current_cluster:
        click.echo("    zkubectl login {}".format(current_cluster))
    click.echo("    zkubectl cluster-access approve {}\n".format(user))


@cluster_access.command('approve')
@click.argument("username", required=True)
@click.pass_obj
def approve_access_request(config, username):
    '''Approve a manual access request'''
    if not username:
        username = click.prompt("User that should receive access")

    existing = access_request.get_all(config).get(username)
    if not existing:
        clickclick.warning("No access requests for {user}".format(user=username))
    elif existing['approved']:
        clickclick.info("Access request for {user} already approved".format(user=username))
    else:
        reason = existing.get('reason', "(no reason provided)")
        if click.confirm("Manual access request from {user}: {reason}. Approve?".format(user=username, reason=reason)):
            updated_reason = access_request.approve(config, username)
            click.echo("Approved access for user {user}: {reason}".format(user=username, reason=updated_reason))


@click_cli.command('approve-manual-access')
@click.argument("username", required=True)
@click.pass_context
def approve_manual_access(ctx, username):
    '''
    DEPRECATED - please use 'cluster-access'.

    DEPRECATED in favor of 'zkubectl cluster-access approve'

    Approve a manual access request
    '''
    clickclick.warning("DEPRECATED in favor of 'zkubectl cluster-access approve'")
    ctx.forward(approve_access_request)


@cluster_access.command('list')
@click.pass_obj
def list_cluster_requests(config):
    '''List all current pending/approved access requests for the cluster'''
    all_requests = access_request.get_all(config)
    access_requests = sorted(all_requests.values(), key=lambda r: r['user'])

    rows = []
    for request in access_requests:
        delta = parse(request['expiry_time']) - datetime.datetime.now(tzutc())
        expiry_time = humanize.naturaldelta(delta)
        request['expires_in'] = expiry_time

        status = "REQUESTED"
        if request.get("approved", False):
            status = "APPROVED"
        request['status'] = status
        rows.append(request)

    print_table(['access_type', 'user', 'reason', 'status', 'expires_in'],
                rows, styles=STYLES, max_column_widths=MAX_COLUMN_WIDTHS)


@click_cli.command('list-access-requests')
@click.pass_context
def list_access_requests(ctx):
    """
    DEPRECATED - please use 'cluster-access'.

    DEPRECATED in favor of 'zkubectl cluster-access list'

    List all current pending/approved access requests for the cluster
    """
    clickclick.warning("DEPRECATED in favor of 'zkubectl cluster-access list'")
    ctx.forward(list_cluster_requests)


@click_cli.command('restart-pods', help="Restart all pods in a deployment.")
@click.argument('target')
@click.option('-n', '--namespace', help='The namespace of the target deployment')
def restart_pods(namespace, target):
    kubectl = ensure_kubectl()
    deployment = Deployment(kubectl, namespace=namespace, name=target)
    annotation_id = str(uuid.uuid4())
    if deployment.ss_ref():
        target_obj = deployment.get_stackset()
    else:
        target_obj = deployment
    try:
        target_obj.annotate_restart(annotation_id)
    except (DeploymentUpdateError, StackUpdateError):
        print('Failed to restart pods for {}'.format(target))
    else:
        print('Successfully patched {} for restart'.format(target))


def main():
    def cleanup_fds():
        # Python tries to flush stdout/stderr on exit, which prints annoying stuff if we get
        # a SIGPIPE because we're piping to head/grep/etc.
        # Close the FDs explicitly and swallow BrokenPipeError to get rid of the exception.
        try:
            sys.stdout.close()
            sys.stderr.close()
        except BrokenPipeError:
            sys.exit(141)

    atexit.register(cleanup_fds)

    try:
        # We need a dummy context to make Click happy
        ctx = click_cli.make_context(sys.argv[0], [], resilient_parsing=True)

        cmd = sys.argv[1] if len(sys.argv) > 1 else None

        if cmd in click_cli.commands:
            click_cli()
        elif not cmd or cmd in click_cli.get_help_option_names(ctx):
            print_help(ctx)
        else:
            kube_config.update_token()
            proxy()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.exit(141)
    except Exception as e:
        clickclick.error(e)
