import os
import sys
import json
import logging

import requests
import yaml
from IPython.core.display import HTML

log = logging.getLogger(__name__)

this = sys.modules[__name__]
this.accessToken = ''
this.api = 'api.mergetb.net'


# =============================================================================
# Developer beware
# !!!!!!!!!!!!!!!!
#
# This librabry will always check for valid SSL certs coming from the API. This
# means that for development, you'll need to import the certificate authority
# cert (not the API cert!) that signed the API cert. If you are using the raven
# development environment this cert is at [px0,px1]:/etc/merge/keys/ca.pem. You
# can instruct requests to honor this cert by setting the environment variable
#
#       REQUESTS_CA_BUNDLE=/<path>/<to>/ca.pem
#
# =============================================================================

# Users ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_users():
    """List users"""
    return do_get('users')

def user_info(user):
    """Get user info

    :param user: user to get info for
    """
    return do_get('users/'+user)

def update_user(user, email, mode):
    """Update user info

    :param user: username to update
    :param email: new user email
    :param mode: access mode (one of public, protected, or private)
    """
    if mode not in ['public', 'protected', 'private']:
        return 400  # bad request.

    return do_post('users/'+user, {
        'username': user,
        'email': email,
        'accessMode': mode,
    })

def user_delete(user):
    """Delete a user

    :param user: user to delete
    """
    return do_delete('users/'+user)

def user_vtoken(user):
    """Get a users validation token

    :param user: user to fetch token for
    """
    return do_get('users/'+user+'/validation_token')

def user_validate(user, token):
    """Validate a user

    :param user: user to validate
    :param token: token to validate with
    """
    return do_post('users/'+user+'/validation_token', {'token': token})

# Sites ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_sites():
    '''List Sites'''
    return do_get('sites')

def new_site(name, fqdn, path):
    """Create a new site

    :param name: new site name
    :param fqdn: new site fully qualified domain name
    :param path: path to file which containes site XIR model (raw json string)
    """

    try:
        with open(path) as fd:
            # GTL TODO: sanitize input.
            model = fd.read()
    except (OSError, ValueError):
        # log this as warn
        return 500

    return do_put('sites/'+name, {
        'name': name,
        'address': fqdn,
        'model': model
    })

def delete_site(name):
    """Delete a site

    :param name: site name to delete
    """

    return do_delete('sites/'+name)

# Health/Status ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def health():
    '''Show health of Merge API'''
    return do_get('health')

# Account Mangement ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def account_init():
    """Ensure my account is initialized"""
    return do_get('user/init')

def account_delete(name):
    """Delete a user account"""
    return do_delete('users/'+name)

# Projects ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_projects():
    '''List Projects user is authorized to view.'''
    return do_get('projects')

def new_project(pid, desc, mode):
    """Define a new project

    :param pid:  new project id
    :param desc: new project description
    :param mode: access mode (one of public, protected, or private)
    """
    return do_put('projects/'+pid, {
        'name': pid,
        'description': desc,
        'accessMode': mode
    })

def update_project(pid, desc, mode):
    """Update a project

    :param pid:  project id
    :param desc: new project description
    :param mode: access mode (one of public, protected, or private)
    """
    return do_post('projects/'+pid, {
        'name': pid,
        'description': desc,
        'accessMode': mode,
    })

def delete_project(pid):
    """Delete a project

    :param pid:  new project id
    """

    return do_delete('projects/'+pid)

def project_info(pid):
    """Get information about the given project

    :param pid: project id
    """
    return do_get('projects/'+pid)

def project_experiments(pid):
    """Get project experiments

    :param pid: project id
    """

    return do_get('/projects/'+pid+'/experiments')

def project_members(pid):
    """Get project members

    :param pid: project id
    """

    return do_get('/projects/'+pid+'/members')

def project_member(pid, mid):
    """Get project member

    :param pid: project id
    :param mid: member id
    """

    return do_get('/projects/'+pid+'/members/'+mid)

def project_add_member(pid, mid, role, state):
    """Get project member

    :param pid: project id
    :param mid: member id
    :param role: member role
    :param state: member state
    """

    return do_put('/projects/'+pid+'/members/'+mid, {
        'member': mid,
        'project': pid,
        'role': role,
        'state': state,
    })

def project_update_member(pid, mid, role, state):
    """Get project member

    :param pid: project id
    :param mid: member id
    :param role: member role
    :param state: member state
    """

    return do_post('/projects/'+pid+'/members/'+mid, {
        'member': mid,
        'project': pid,
        'role': role,
        'state': state,
    })

def project_delete_member(pid, mid):
    """Get project member

    :param pid: project id
    :param mid: member id
    """

    return do_delete('/projects/'+pid+'/members/'+mid)

# Experiments ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_experiments(pid):
    """List the experiments of a project

    :param pid:  project to which experiments belong
    """

    return do_get('/projects/'+pid+'/experiments')

def new_experiment(pid, eid, desc):
    """Define a new experiment

    :param pid: existing project id
    :param eid: new experiment id
    :param desc: new experiment description
    """

    return do_put('projects/'+pid+'/experiments/'+eid, {
        'name': eid,
        'description': desc
    })

def delete_experiment(pid, eid):
    """Delete an experiment

    :param pid: project id
    :param eid: experiment id
    """

    return do_delete('projects/'+pid+'/experiments/'+eid)

def update_experiment(pid, eid, desc):
    """Update an experiments information.

    :param pid:  project id
    :param eid:  experiment id
    :param desc: new project description
    """
    return do_post('/projects/{}/experiments/{}'.format(pid, eid), {
        'name': eid,
        'description': desc,
    })

def push_experiment(pid, eid, src):
    """Push a new version of the experiment source code

    :param pid: project id
    :param eid: experiment id
    :param src: the xir
    """

    return do_post('projects/'+pid+'/experiments/'+eid+'/src', {
        'src': src
    })

def push_experiment_file(pid, eid, path):
    """Push a new version of the experiment source code

    :param pid: project id
    :param eid: experiment id
    :param path: the path to the xir file to push
    """
    with open(path) as fd:
        src = fd.read()
        return do_post('projects/'+pid+'/experiments/'+eid+'/src', {
            'src': src
        })
    return None

def experiment_history(pid, eid):
    """Get the experiment version history

    :param pid: project id
    :param eid: experiment id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/src')

def experiment_info(pid, eid):
    """Get information about the given experiment

    :param pid: project id
    :param eid: experiment id
    """
    return do_get('projects/'+pid+'/experiments/'+eid)

# Realizations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def realize(pid, eid, name, hsh):
    """Realize an experiment.

    On success the resources that underpin the realization will be yours for
    the next 47 seconds. Use accept() on the realization hash id to claim the
    realization until you decide to explicitly release it or the maximum lease
    on the resources runs up. Alternatively use reject() to free the resources
    and destroy the realization immediately.

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    :param name: experiment version hash
    """

    return do_put('projects/'+pid+'/experiments/'+eid+'/realizations/'+name, {
        'name': name,
        'hash': hsh
    })

def list_realizations(pid, eid):
    """List the realizations associated with an experiment

    :param pid: project id
    :param eid: experiment id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations')

def get_realization(pid, eid, name):
    """Get the details of a realization.

    Returns a json object with the nitty gritty.

    :param pid: project id
    :param ied: experiment id
    :param name: realization name
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+name)


def accept_realization(pid, eid, name):
    """Accept a realization.

    Upon accepting a realization, the resources are yours until you explicitly
    let them go or the lease runs out on any resource in the realization,
    whichever comes first.

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    """

    return do_post(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+name+'/act',
        {'action': 'accept'}
    )

def reject_realization(pid, eid, name):
    """Reject a realization.

    Reject a realization, short circuiting the 47 second timeout. Only a
    realization in the pending state may be rejected. Realizations that
    have been accepted can be destroyed through unrealize()

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    """

    return do_post(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+name+'/act',
        {'action': 'reject'}
    )

def delete_realization(pid, eid, name):
    """Delete a realization.

    This will free all resources associated with a realization. If there is an
    active materialization associated with the realization, it will be
    clobbered.

    :param pid: project id
    :param eid: experiment id
    :param name: realization name
    """

    return do_delete('projects/'+pid+'/experiments/'+eid+'/realizations/'+name)


# Materializations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_materializations(pid, eid, rid):
    """List the materializations associated with an experiment

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
                  '/materializations/')

def get_materialization(pid, eid, rid, name):
    """Get a materialization.

    Fetch the nitty gritty.

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    :param name: materialization name
    """

    return do_get('projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
                  '/materializations/'+name)


def materialize(pid, eid, rid, name):
    """Materialize a realization.

    This will start the process of turning your experiment into a ticking
    breathing monster. The nodes will be brought online and imaged, and the
    your networks synthesized and isolated.

    :param pid: project id
    :param eid: experiment id
    :param rid: realization id
    :param name: materialization name
    """

    res = do_put(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
        '/materializations/'+name,
        {}
    )
    return res

def dematerialize(pid, eid, rid, name):
    """Dematerialize a realization.

    This will tear all the resources in a materialization down to a zero state.
    This does not relinquish the resources, they are still yours, so you can
    materialize again if so desired.

    :param pid: project id
    :param eid: experiment id
    :param name: realiztaion id
    """

    print("dematerializing %s/%s/%s"%(pid, eid, rid))
    res = do_delete(
        'projects/'+pid+'/experiments/'+eid+'/realizations/'+rid+
        '/materializations/'+name
    )
    print("your experiment has vaporized")
    return res

# xdcs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def list_xdcs(pid, eid):
    """List the experiment development containers associated with an experiment

    :param pid: project id
    :param eid: experiment id
    """

    return do_get('/projects/'+pid+'/experiments/'+eid+'/xdc')

def spawn_xdc(pid, eid, name):
    """Spawn an experiment development contianer

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc to spawn
    """
    return do_put('/projects/'+pid+'/experiments/'+eid+'/xdc/'+name, None)

def destroy_xdc(pid, eid, name):
    """Destroy an experiment development contianer

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc to spawn
    """
    return do_delete('/projects/'+pid+'/experiments/'+eid+'/xdc/'+name)

def xdc_token(pid, eid, name):
    """Get an experiment development containers Jupyter access token

    :param pid: project id
    :param eid: experiment id
    :param name: name of the xdc to spawn
    """
    return do_get('/projects/'+pid+'/experiments/'+eid+'/xdc/'+name+'/token')

# pubkeys ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def list_pubkeys(uid):
    """Get a users public keys

    :param uid: user id
    """

    return do_get('/users/'+uid+'/keys')

def add_pubkey(uid, keyfile):
    """Add a public key for the user

    :param uid: user id
    :keyfile: pubkey file
    """

    with open(keyfile, 'r') as f:
        text = f.read().replace('\n', '')

    return do_put('/users/'+uid+'/keys', {
        "key": text,
    })

def delete_pubkey(uid, fingerprint):
    """Delete a public key for the user

    :param uid: user id
    :param fingerprint: md5 ssh key fingerprint
    """

    return do_delete('/users/'+uid+'/keys/'+fingerprint)


# helpers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def show(thing):
    print(yaml.dump(yaml.load(json.dumps(thing)), default_flow_style=False))

def do_get(path):
    '''GET a path on the merge API and return the results.

    :param path: the path to GET
    '''
    try:
        resp = requests.get(
            'https://'+this.api+'/'+path,
            headers={'authorization': 'Bearer ' + this.accessToken}
        )
    except ConnectionError as e:
        log.critical('Error connection to API: %s', e)
        return None

    if resp.ok:
        try:
            return resp.json()
        except ValueError:
            # Not JSON, so just return the status code.
            pass

    return resp.status_code

def do_put(path, payload):
    try:
        if payload:
            resp = requests.put(
                'https://'+this.api+'/'+path,
                headers={'authorization': 'Bearer ' + this.accessToken},
                json=payload
            )
        else:
            resp = requests.put(
                'https://'+this.api+'/'+path,
                headers={'authorization': 'Bearer ' + this.accessToken},
            )
    except ConnectionError as e:
        log.critical('put %s connection error: %s', path, e)
        return "500: internal error"

    if resp.status_code == 200:
        return "ok"

    return "%d: %s"%(resp.status_code, resp.text)

def do_put_file(url, filepath):
    '''Call a Merge API endpoint with PUT and the given payload as the body.

    Errors in JSON payload or reading the filepath will result in a 500 error
    returned.

    :param url: the API endpoint
    :param filepath: The file which contains the message body (in JSON).
                     Invalid JSON will not be sent.
    '''
    try:
        with open(filepath) as fd:
            # GTL TODO: sanitize input.
            payload = json.load(fd)
            return do_put(url, payload)
    except (OSError, ValueError):
        # log this as warn
        pass
    return 500

def do_post_file(url, filepath):
    '''Call a Merge API endpoint with cwPOSTPUT and the given payload as the body.

    Errors in JSON payload or reading the filepath will result in a 500 error
    returned.

    :param url: the API endpoint
    :param filepath: The file which contains the message body (in JSON).
                     Invalid JSON will not be sent.
    '''
    try:
        with open(filepath) as fd:
            # GTL TODO: sanitize input.
            payload = json.load(fd)
            return do_post(url, payload)
    except (OSError, ValueError):
        # log this as warn
        pass
    return 500

def do_post(path, payload):
    resp = requests.post(
        'https://'+this.api+'/'+path,
        headers={'authorization': 'Bearer ' + this.accessToken},
        json=payload,
    )
    return resp.status_code

def do_delete(path):
    resp = requests.delete(
        'https://'+this.api+'/'+path,
        headers={'authorization': 'Bearer ' + this.accessToken},
    )
    return resp.status_code

def set_token(token):
    """Set the OAuth2 access token used to access the mergetb API"""
    this.accessToken = token

def set_api(api):
    """Set the mergetb API url"""
    this.api = api

def fetch_web_token():
    """For use in Jupyter environment only. If you've logged in via the
    mergetb login page in the browser, this function will fetch and
    set the corresponding oauth access token from the browser.
    """

    js = """
    <script type="text/javascript">
    var tk = localStorage.getItem("accessToken");
    var cmd = "mergetb.set_token('"+tk+"')";
    var kernel = IPython.notebook.kernel;
    kernel.execute(cmd);
    </script>
    """
    return HTML(js)

def fetch_fs_token():
    with open(os.path.expanduser('~')+'/.merge/token', 'r') as f:
        token = f.read()

    set_token(token)

# TODO delete me
# pylint: disable=wrong-import-position
from IPython import get_ipython
def init():
    ipython = get_ipython()
    ipython.magic("env REQUESTS_CA_BUNDLE=/home/ry/scratch/pem/ca.pem")
    fetch_fs_token()
    set_api('api.mergetb47.net')
