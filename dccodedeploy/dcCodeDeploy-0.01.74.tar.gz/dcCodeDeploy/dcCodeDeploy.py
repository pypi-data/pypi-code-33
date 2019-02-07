#
# Django Code Deploy
#
# Copyright 2015 - 2018 devops.center llc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

from fabric.api import *

from time import gmtime, strftime
import os
import sys
from git import Repo
import distutils.sysconfig
from instanceinfo import InstanceInfo


# Use bash for fabric local commands, per
# http://www.booneputney.com/development/fabric-run-local-bash-shell/
from fabric.api import local as local_cmd  # import local with alternate name

# create new local command, with the shell set to /bin/bash


def local(command_string):
    local_cmd(command_string, shell="/bin/bash")


class FabricException(Exception):
    pass

TRUTH_VALUES = ['True', 'TRUE', '1', 'true', 't', 'Yes',
                'YES', 'yes', 'y']  # arguments in fab are always strings

# Set some global defaults for all operations.
# These ones may be modified by an ENV var.
#
env.connection_attempts = os.getenv('dcCodeDeployConnectionAttempts', 3)

dcSharedDir=os.getenv('dcSharedDir', '~')

#
# These settings may be altered either via an ENV var or via a fab task.
#

#
# Allow different users for target instance access.
#
env.user = os.getenv('dcCodeDeployUser','ubuntu')

@task
def set_user(loginName):
    env.user = loginName

#
# Allow different organization (customer) for target instance access.
#
ORG = os.getenv('dcCodeDeployOrg','')

@task
def set_org(organization):
    global ORG
    ORG = organization


#
# Look for this setting from the calling environment. 
# E.g. for Jenkins. Note that in any Jenkins job, environment variables can come from one of three places:
#     globally (from manage Jenkins, global properties)
#     per job, via either a bash export at the beginning of the job or the environment injector plugin,
#     per fab invocation, via the follow set_ip_mode fab task.
# If this doesn't make any sense, well ....
#
IP_MODE=os.getenv('dcCodeDeployIPMode', 'public')

@task
def set_ip_mode(mode):
    global IP_MODE
    if mode in ['public', 'private']:
        IP_MODE = mode

#
#  Establish either an individual ssh key, or a path for all private ssh keys.
#
env.key_filename=os.getenv('dcCodeDeployKeyFilename','')

@task
def set_access_key(accessKey):
    env.key_filename = [accessKey]

#
#  Establish either an individual ssh key, or a path for all private ssh keys.
#
ENVIRONMENT=os.getenv('dcCodeDeployEnvironment','')

@task
def set_environment(this_environment):
    global ENVIRONMENT
    ENVIRONMENT = this_environment


ACCESS_KEY_PATH=os.getenv('dcCodeDeployKeyPath', '~/.ssh')

@task
def set_access_key_path(anAccessKeyPath):
    global ACCESS_KEY_PATH
    if(anAccessKeyPath.endswith('/')):
        ACCESS_KEY_PATH = anAccessKeyPath
    else:
        ACCESS_KEY_PATH = anAccessKeyPath + "/"


# deploy directories have timestamps for names.
timest = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
UPLOAD_CODE_PATH = os.path.join("/data/deploy", timest)
TAR_NAME = "devops"

#
# set_hosts selects all instances that match the filter criteria.
#  type is web, worker, db
#  environment is dev, staging, prod
#  appname is application name, such as "fresco", "topopps", "mojo", etc.
#  action is the deferred action needed, such as "deploy", "security-updates", etc.
#  region is aws region
@task
def set_hosts(type, primary=None, appname=None, action=None, region=None,
              shard=None, aRole=None):

    regions = [e for e in region.split(' ')] if region else []

    instances = InstanceInfo(ORG, ACCESS_KEY_PATH, regions, dcSharedDir)

    tags={}
    if type:
        tags["Type"] = [e for e in type.split(' ')]
    tags["Env"] = [ENVIRONMENT]
    tags["App"] = [appname]
    if action:
        tags["Action"] = [action]
    if aRole:
        tags["role"] = [aRole]
    if shard:
        tags["Shard"] = [e for e in shard.split(' ')]

    targets = instances.getInstanceInfo(tags)

# Require all destination instances to use the same jump server (gateway), login (user), and target port.
    for instance in targets:
        env.gateway = instances.getGatewayInfo(instance)
        if instance.DestLogin:
            env.user = instance.DestLogin
        if (IP_MODE == 'public') and instance.PublicPort:
            env.port = instance.PublicPort
        elif instance.PrivatePort:
            env.port = instance.PrivatePort

    env.hosts = [instance.PublicIpAddress if ((IP_MODE == 'public') and instance.PublicIpAddress) else instance.PrivateIpAddress for instance in targets]
    env.host_names = [instance.InstanceName for instance in targets]
    env.key_filename = instances.getListOfKeys()

    _log_hosts(targets)


# set_one_host picks a single instance out of the set.
#  filters are the same as with set_hosts.
@task
def set_one_host(type, primary=None, appname=None, action=None, region=None,
                 shard=None, aRole=None):

    regions = [e for e in region.split(' ')] if region else []
    instances = InstanceInfo(ORG, ACCESS_KEY_PATH, regions, dcSharedDir)

    tags={}
    if type:
        tags["Type"] = [e for e in type.split(' ')]
    tags["Env"] = [ENVIRONMENT]
    tags["App"] = [appname]
    if action:
        tags["Action"] = [action]
    if aRole:
        tags["role"] = [aRole]
    if shard:
        tags["Shard"] = [e for e in shard.split(' ')]
 
    targets = instances.getInstanceInfo(tags)
    instance = targets[0]
    targets = [instance]

    env.gateway = instances.getGatewayInfo(instance)
    if instance.DestLogin:
        env.user = instance.DestLogin
    if (IP_MODE == 'public') and instance.PublicPort:
        env.port = instance.PublicPort
    elif instance.PrivatePort:
        env.port = instance.PrivatePort
    env.hosts = [instance.PublicIpAddress if ((IP_MODE == 'public') and instance.PublicIpAddress) else instance.PrivateIpAddress]
    env.host_names = [instance.InstanceName]
    env.key_filename = instance.DestKey


    _log_hosts(targets)


@task
def set_one_host_per_shard(type, primary=None, appname=None, action=None,
                           region=None, shard=None, aRole=None):

    regions = [e for e in region.split(' ')] if region else []
    instances = InstanceInfo(ORG, ACCESS_KEY_PATH, regions, dcSharedDir)

    tags={}
    if type:
        tags["Type"] = [e for e in type.split(' ')]
    tags["Env"] = [ENVIRONMENT]
    tags["App"] = [appname]
    if action:
        tags["Action"] = [action]
    if aRole:
        tags["role"] = [aRole]
    if shard:
        tags["Shard"] = [e for e in shard.split(' ')]
 
    targets = instances.getInstanceInfo(tags)

# Remove any duplicate hosts from each shard, leaving only one per shard
    pruned_list = []
    for ahost in targets:
        if not any(ahost.Shard == bhost.Shard for bhost in pruned_list):
            pruned_list.append(ahost)
    targets = pruned_list

# Require all destination instances to use the same jump server (gateway) and use the same login (user)
    for instance in targets:
        env.gateway = instances.getGatewayInfo(instance)
        if instance.DestLogin:
            env.user = instance.DestLogin
        if (IP_MODE == 'public') and instance.PublicPort:
            env.port = instance.PublicPort
        elif instance.PrivatePort:
            env.port = instance.PrivatePort

    env.hosts = [instance.PublicIpAddress if ((IP_MODE == 'public') and instance.PublicIpAddress) else instance.PrivateIpAddress for instance in targets]
    env.host_names = [instance.InstanceName for instance in targets]
    env.key_filename = instances.getListOfKeys()

    _log_hosts(targets)


def _log_hosts(instances):
    logger.info("")
    logger.info(
        "Instances to operate upon - name, public ip, private ip, shard")
    logger.info(
        "---------------------------------------------------------------")
    for instance in instances:
        logger.info("%s  %s  %s  %s", instance.InstanceName,
                    instance.PublicIpAddress, instance.PrivateIpAddress, instance.Shard)
    logger.info("")
    logger.info("")
    logger.info("keys: %s", env.key_filename)
    logger.info("hosts: %s", env.hosts)
    logger.info("host_names: %s", env.host_names)
    logger.info("gateway: %s", env.gateway)
    logger.info("user: %s", env.user)
    logger.info("")


# These are tasks for building on jenkins (or other build box)
# Initally support a yarn-based workflow for node


@task
def build(branch, installPath, node=False, angularBuild=False):


    # ensure yarn installs all build tools
    with lcd(installPath):
        local("pwd")
        local('yarn --production=false --no-progress --non-interactive install')

        # do the build
        if angularBuild:
            local(
                'npm run build -- --prod --configuration=%s && cp -r public/* dist/' % ENVIRONMENT)
        else:
            local('npm run dist')

        if node in TRUTH_VALUES:
            local(
                'if [[ -d "config" ]]; then echo "<collecting config>" ; rsync -ra --stats config/ dist/config; fi;')
            local(
                'if [[ -d "src/public" ]]; then echo "<collecting public>" ; rsync -ra --stats src/public/ dist/public; fi;')


    # make sure the new files are part of the local git repo
    local('find . -path ./\.git -prune -o -name \.gitignore -type f -exec rm -f {} \;')
    local('echo "%s.tar.*" >> .gitignore' % TAR_NAME)
    local('echo "fabfile.*" >> .gitignore')
    local("git add .")
    local("git commit -am 'add results of build' --no-verify --quiet")


# Obtain git_sha from Jenkins git plugin, make sure it's passed along with the code so that
# uwsgi, djangorq, and and celery can make use of it (e.g. to pass to
# Sentry for releases)

@task
def set_git_sha():
    local('echo "GIT_SHA=${GIT_COMMIT}" >> dynamic_env.ini')
    local('git add .')


@task
def tar_from_git(branch, dirs=None):
    local("pwd")
    if dirs:
        local('tar -czf %s.tar.gz %s' % (TAR_NAME, dirs))

    else:
        local('find . -path ./\.git -prune -o -name \.gitignore -type f -exec rm -f {} \;')
        local('echo "%s.tar.*" >> .gitignore' % TAR_NAME)
        local('echo "fabfile.*" >> .gitignore')
        local('rm -rf %s.tar.gz' % TAR_NAME)
        local('git archive %s --format=tar.gz --output=%s.tar.gz' %
              (branch, TAR_NAME))


@task
def clean_up():
    local('git reset --hard ${GIT_COMMIT}')
    local('git clean -fdq')


@task
def unpack_code():
    cmd = "mkdir -p " + UPLOAD_CODE_PATH
    sudo(cmd)
    put('%s.tar.gz' % TAR_NAME, '%s' % UPLOAD_CODE_PATH, use_sudo=True)
    with cd('%s' % UPLOAD_CODE_PATH):
        sudo('tar zxf %s.tar.gz' % TAR_NAME)


@task
def link_new_code():
    try:
        sudo('unlink /data/deploy/pending')
    except:
        pass
    sudo('ln -s %s /data/deploy/pending' % UPLOAD_CODE_PATH)

    with cd('/data/deploy'):
        # keep onlly 5 most recent deploys, excluding any symlinks or other purely alpha directories. The steps are
        #  1. generate list of directories, sorted by modification time.
        #  2. reemove anything thay does not have a "20" in it, e.g. the millenia (leftmost 2 digits of the 4 digit year)
        #  3. keep the 5 most recent - these become the ones to keep.
        #  4. add a listing of all directories to these top 5.
        #  5. sort the combined listing
        #  6. keep only directory names that are *not* repeated - so this will be all directories beyond those first 5 numeric directories.
        #  7. filter out any alpha directories that were added by the second ls.
        #  8. remove all of the directories that remain.
        sudo('(ls -t|grep 20|head -n 5;ls)|sort|uniq -u|grep 20|xargs rm -rf')


@task
def pip_install():
    with cd('/data/deploy/pending'):
        sudo('if [[ -f requirements.txt ]]; then pip install -r requirements.txt; fi')


@task
def yarn_install(installPath):

    try:
        with cd("/data/deploy/pending/%s" % installPath):
            sudo('yarn --no-progress --non-interactive install')
    except FabricException:
        pass


@task
def download_nltk_data():
    run("echo 'loading NLTK data specified in nltk.txt'")
    sudo_app(
        'if [[ -f nltk.txt ]]; then mkdir -p /usr/share/nltk_data/; cat nltk.txt | while read -r line; do python -m nltk.downloader -d /usr/share/nltk_data ${line}; done; fi')


@task
def collect_static():
    with cd('/data/deploy/pending'):
        sudo('if [[ ! -d static ]]; then mkdir static/ ;fi')
        sudo('chmod 777 static')
        sudo('python manage.py collectstatic --noinput')


@task
# https://docs.djangoproject.com/en/1.8/ref/django-admin/#django-admin-check
def django_check():
    with cd('/data/deploy/pending'):
        sudo('python manage.py check')


@task
def remote_inflate_code():
    unpack_code()
    link_new_code()
    codeversioner()


@task
def codeversioner():
    repo = Repo('.')
    headcommit = repo.head.commit
    commitid = headcommit.hexsha
    versionhash = commitid
    print versionhash
    with cd('/data/deploy/pending'):
        run("echo 'version=\"%s\"' > /tmp/versioner.py" % versionhash)
        cmd = 'cp /tmp/versioner.py /data/deploy/pending/versioner.py'
        sudo(cmd)


# This assumes the local repo is ready (any build has been done and
# commited), then creates the tarball, finally deploys one at a time
@task
def deploycode(branch, nltkLoad="False", doCollectStatic="True", yarn="False", immutable="True"):
    tar_from_git(branch)
    remote_inflate_code()

    if not yarn in TRUTH_VALUES:
        pip_install()

    if nltkLoad in TRUTH_VALUES:
        download_nltk_data()

 # Either do a django collectstatic, or at least collect django admin
 # static assets (except for yarn deploys)
    if doCollectStatic in TRUTH_VALUES:
        collect_static()
    else:
        if not yarn in TRUTH_VALUES:
            sudo('cp -r ' + '/usr/local/opt/python/lib/python2.7/site-packages' +
                 '/django/contrib/admin/static/admin /data/deploy/pending/static/')

    if not immutable in TRUTH_VALUES:
        with cd('/data/deploy/pending'):
            sudo('sudo chown -R ubuntu:ubuntu *')


# This deploy assumes the tar ball ha been created (and any build steps
# done prior), then deploys all targets in parallel
@task
@parallel
def deployParallel(nltkLoad="False", doCollectStatic="True", yarn="False", immutable="True"):
    remote_inflate_code()

    if not yarn in TRUTH_VALUES:
        pip_install()

    if nltkLoad in TRUTH_VALUES:
        download_nltk_data()

# Either do a django collectstatic, or at least collect django admin
# static assets (except for yarn deploys)
    if doCollectStatic in TRUTH_VALUES:
        collect_static()
    else:
        if not yarn in TRUTH_VALUES:
            sudo('cp -r ' + '/usr/local/opt/python/lib/python2.7/site-packages' +
                 '/django/contrib/admin/static/admin /data/deploy/pending/static/')

    if not immutable in TRUTH_VALUES:
        with cd('/data/deploy/pending'):
            sudo('sudo chown -R ubuntu:ubuntu *')


@task
def dbmigrate_node(installPath):

    pathToUse = '/data/deploy/pending/' + installPath + "/dist"

    with cd(pathToUse):
        run('pwd')
        run('npm run migrate')


@task
def rollback_dbmigrate_node(installPath):

    pathToUse = '/data/deploy/pending/' + installPath + "/dist"

    with cd(pathToUse):
        run('pwd')
        run('npm run rollback')


@task
@parallel
def dbmigrate(migrateOptions=None):
    cmdToRun = "cd /data/deploy/pending && python manage.py migrate --noinput"

    if migrateOptions is not None:
        cmdToRun += " " + migrateOptions

    run(cmdToRun)

# todo: deprecate this task


@task
def dbmigrate_docker(containerid, codepath='/data/deploy/current'):
    run('docker exec -it %s /bin/bash -c "cd /data/deploy/current && python manage.py migrate --noinput --ignore-ghost-migrations"' % containerid)


#
# These atomic tasks for putting the new deploy into effect are preferred, as they
# may run in parallel, while minimizing the exposure between the swap_code and putting the new code into effect
#
supervisor = "/usr/bin/supervisorctl"


@task
@parallel
def update_app_utils(appname, branch, reboot=False):
    # tar up the app-util code with only the environment and config directory
    local("pwd")
    # need to check to see if they are using dcShared-utils
    APP_UTILS_DIR = appname + "-utils"
    if not os.path.isdir(APP_UTILS_DIR):
        # it's not in the current directory so it must be under the dcShared-utils directory
        lcd("dcShared-utils")
    
    # tar it up
    TAR_NAME = "app-utils"
    CONFIG_DIR = APP_UTILS_DIR + "/config"
    ENV_DIR = APP_UTILS_DIR + "/environments"
    DIRS_TO_TAR = CONFIG_DIR + " " + ENV_DIR
    print(DIRS_TO_TAR)

    local('git archive %s --format=tar.gz --output=%s.tar.gz %s %s' % (branch, TAR_NAME, CONFIG_DIR, ENV_DIR))

    # and move the tarball to the destination and expand it
    # set the upload path to the home directory
    UPLOAD_CODE_PATH = "$HOME/" + appname 
    cmd = "mkdir -p " + UPLOAD_CODE_PATH
    sudo(cmd)
    with cd('%s' % UPLOAD_CODE_PATH):
        put('%s.tar.gz' % TAR_NAME, '%s.tar.gz' % TAR_NAME, use_sudo=True)
        run('tar zxf %s.tar.gz' % TAR_NAME)

    # run the "instanceType"-command.sh in the appropriate branch
    cmdToRun = "$HOME/" + appname + "/" + APP_UTILS_DIR + "/config/" + ENVIRONMENT + "/${dc_TAG_Type}-commands.sh"
    sudo(cmdToRun)

    # run deployenv on the instance to get the new values into /etc/enviornmnet
    run("deployenv.sh --type instance -a " + appname + " -e " + ENVIRONMENT)

    if reboot:
        # and reboot to make sure the enviornment is read with the new enviornment variables before the services start
        with settings(hide('warnings'), warn_only=True):
            sudo("shutdown -r now")


@task
def swap_code():
    try:
        sudo('unlink /data/deploy/current')
    except:
        pass

    sudo("ln -s $(readlink /data/deploy/pending) /data/deploy/current")

@task
def rollback_code():
#    with settings(hide('warnings'), warn_only=True):
#        sudo('unlink /data/deploy/current')
#        sudo('unlink /data/deploy/pending')

    with settings(shell_escape=False, warn_only=True):
        t=run("ls -t|grep 20|head -2|ls|grep 20|sort -r|head -2|tail -1|xargs -I \\% sudo ln -s /data/deploy/\\% /data/deploy/current")
        logger.info("real: %s",t.real_command)
        logger.info("cmd:  %s",t.command)  

#        t=run("ls -t|grep 20|head -2|ls|grep 20|sort -r|head -2|tail -1|xargs -I \\% sudo ln -s /data/deploy/\\% /data/deploy/pending")
#        logger.info("real: %s",t.real_command)
#        logger.info("cmd:  %s",t.command)  

#       t=run("ls -t|grep 20|head -2|ls|grep 20|sort -r|head -1 |xargs -I \\% sudo rm -rf \\%")  
#        logger.info("real: %s",t.real_command)
#        logger.info("cmd:  %s",t.command)  


@task
@parallel
def reload_web(doCollectStatic=None,nginxOnly=False):
    swap_code()
    if doCollectStatic in TRUTH_VALUES:
        collect_static()

    reload_nginx()

    if not nginxOnly in TRUTH_VALUES:
        reload_uwsgi()


@task
@parallel
def restart_web(doCollectStatic=None,nginxOnly=False):
    swap_code()
    if doCollectStatic in TRUTH_VALUES:
        collect_static()

    restart_nginx()

    if not nginxOnly in TRUTH_VALUES:
       restart_uwsgi()


@task
@parallel
def reload_worker(async="djangorq", doCollectStatic=None):
    swap_code()
    if doCollectStatic in TRUTH_VALUES:
        collect_static()

    if async == "djangorq":
        reload_djangorq()
    elif async == "celery":
        restart_celery()
    else:
        logger.info("Specified async facility not supported")


@task
@parallel
def restart_worker(async="djangorq", doCollectStatic=None):
    swap_code()
    if doCollectStatic in TRUTH_VALUES:
        collect_static()

    if async == "djangorq":
        restart_djangorq()
    elif async == "celery":
        restart_celery()
    else:
        logger.info("Specified async facility not supported")


@task
@parallel
def reload_node(processName):
    swap_code()

    sudo("%s restart %s" % (supervisor, processName))


@task
def reload_nginx():
    swap_code()

    sudo("/usr/local/nginx/sbin/nginx -s reload")


#
# All reloads and restarts below this do not have an implied swap_code
#

@task
def reload_uwsgi():
    sudo("/bin/bash -c 'echo c > /tmp/uwsgififo'")


@task
def reload_djangorq():
    sudo(
        "for process in $(ps -ef|grep rq|grep -v grep|awk '{print $2}'); do kill -INT ${process}; done")


@task
def restart_nginx():
    sudo("%s restart nginx" % supervisor)


@task
def restart_uwsgi():
    sudo("mkdir -p /var/run/uwsgi")
    sudo("%s restart uwsgi" % supervisor)


@task
def restart_celery():
    sudo("%s restart celery:*" % supervisor)


@task
def restart_djangorq():
    sudo("%s restart djangorq-worker:*" % supervisor)


@task
def restart_pgpool():
    sudo("%s restart pgpool" % supervisor)


@task
def restart_php():
    sudo("%s restart php:php_00" % supervisor)


@task
def run_cmd(cmdToRun):
    run(cmdToRun)


@task
def sudo_cmd(cmdToRun):
    sudo(cmdToRun)


@task
def run_app(cmdToRun, stopOnError="True"):
    if stopOnError in TRUTH_VALUES:
        with cd('/data/deploy/pending'):
            run(cmdToRun)
    else:
        with settings(abort_exception=FabricException):
            try:
                with cd('/data/deploy/pending'):
                    run(cmdToRun)
            except FabricException:
                pass

@task
def sudo_app(cmdToRun, stopOnError="True"):
    if stopOnError in TRUTH_VALUES:
        with cd('/data/deploy/pending'):
            sudo(cmdToRun)
    else:
        with settings(abort_exception=FabricException):
            try:
                with cd('/data/deploy/pending'):
                    sudo(cmdToRun)
            except FabricException:
                pass

@task
def put_files(src,dest):
    put(src,dest)

