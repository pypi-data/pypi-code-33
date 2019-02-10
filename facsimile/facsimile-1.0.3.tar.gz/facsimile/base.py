#!/usr/bin/env python
##########################################################################

from optparse import OptionParser, OptionGroup
import errno
import os
import os.path
import re
import platform
import pprint
import shlex
import shutil
import stat
import subprocess
import sys
import inspect
import getpass
import subprocess
import hashlib
import time
import twentyc.tmpl

import codec
from .definition import Definition
from .state import State
from .install import Install
from functools import reduce

##########################################################################


class FileCompare(object):

    def __init__(self, base):
        self.base = base
        self.files = set()

    def add_file(self, filename):
        self.files.add(filename)

    def check(self, targets, user, host):
        cf = self.base.defined["deploy"]

        args = ['ssh', '%s@%s' % (
            user, host), "sh -c 'for file in %s ; do if [ -f $file ] ; then echo $file ;  fi ; done'" % (' '.join(self.files))]
        rv, out, err = self.base.call_get_output(args)
        if rv or err:
            raise RuntimeError(
                "could not check remote files for host %s. rv %d err %s" % (host, rv, err))

        has = set()
        for filename in out.split('\n'):
            if filename:
                has.add(filename)

        ignore_set = set()

        if 'libcheck_ignorelist' in cf:
            ign = cf['libcheck_ignorelist']
            for target in targets:
                if target in ign:
                    for fn in ign[target]:
                        ignore_set.add(fn)

        missing = self.files - has - ignore_set

        if missing:
            for missed in missing:
                print 'libcheck FAILURE for presence of %s on %s' % (missed, host)
            return False
        else:
            print 'libcheck ok for %s' % host
            return True

default_top_dir = os.path.join(os.getcwd(), '.facsimile')

class Base(object):

    summary_attrs=['release_environment', 'version', 'script_dir', 'top_dir', 'define_dir', 'deploy_dir', 'build_dir', 'release_dir', 'src_dir', 'state_dir', 'deploy_dir', 'repo']
    """ display these attributes in summary"""

    en_write_version=True
    """ write a version file to be deployed """

    __fixed_attrs=['name', 'release_environment', 'version', 'top_dir']

    # general options
    __clean = False
    __debug = False
    __chatty = False
    __devel = False
    __dry_run = False

    # build options
    __build_docs = False
    __release = False
    __static = False
    __skip_unit = False

    __run = []

    @property
    def stage_start(self):
        return self.__stage_start

    @property
    def stage_end(self):
        return self.__stage_end

    @property
    def clean(self):
        return self.__clean

    @property
    def dry_run(self):
        return self.__dry_run

    @property
    def is_debug(self):
        return self.__debug

    @property
    def is_devel(self):
        return self.__devel

    @property
    def skip_unit(self):
        return self.__skip_unit

    @property
    def skip_libcheck(self):
        return self.__skip_libcheck

    @property
    def with_debuginfo(self):
        return self.__debuginfo

    @property
    def build_docs(self):
        return self.__build_docs

    @property
    def is_release(self):
        return self.__release

    @property
    def is_static(self):
        return self.__static

    @property
    def make_dash_j(self):
        return self.__make_dash_j

    @property
    def is_unixy(self):
        # OSXFIXME
        if sys.platform.startswith("linux"):
            return True
        return False

    @property
    def is_64b(self):
        # OSXFIXME
        return '64' in platform.machine()

    @property
    def sys_bits(self):
        return 64 if self.is_64b else 32

    @property
    def build_name(self):
        return "%s-%s-%dbit-%s%s" % (self.version, self.system, self.bits, self.compilertag, self.build_suffix)

    def __init__(self, **kwargs):
        self.script_dir = os.path.join(os.path.dirname(__file__), "script")
        self._install = Install(self)

        # required
        for attr in self.__fixed_attrs:
            self._get_init_var(kwargs, attr)

        # defaults
        if not hasattr(self, 'version'):
            # TODO - HEAD
            self.version = ''
        if not hasattr(self, 'top_dir'):
           self.top_dir = default_top_dir

        self.sanity_check()

        # - build
        # is_devel
        # system
        # bits
        # build suffix
        # compiler tag

        self.tmp_dir = os.path.join(self.top_dir, "tmp")
        self.top_src_dir = os.path.join(self.tmp_dir, "SRC")
        self.top_build_dir = os.path.join(self.tmp_dir, "BUILD")
        self.top_release_dir = os.path.join(self.tmp_dir, "RELEASE")

        self.ver_name = "%s-%s" % (self.name, self.version)
        src_dir = kwargs.get('src_dir', None)
        if src_dir:
            self.src_dir = src_dir
            kwargs['devel'] = True
            self.__nocheckout = True
        else:
            self.src_dir = os.path.join(self.top_src_dir, self.ver_name)
            self.__nocheckout = False

        #   define dir
        self.define_dir = kwargs.get('define_dir', self.find_define_dir())

        # top state dir loaded from 'state_dir' for later changes
        self.top_state_dir = kwargs.get('state_dir', os.path.join(self.top_dir, "state"))

        self.add_config(kwargs)

        # exec derived class system specific function
        if hasattr(self, "_init_" + self.system):
            return getattr(self, "_init_" + self.system)()

        self._init_dirs()

    def _get_init_var(self, config, key):
        var = config.pop(key, None)
        if var:
            setattr(self, key, var)

    def add_config(self, config):
        """
        Update internel configuration dict with config and recheck
        """
        for attr in self.__fixed_attrs:
            if attr in config:
                raise Exception("cannot set '%s' outside of init", attr)

        # pre checkout

        stages = config.get('stages', None)
        if stages:
            self.stages = stages

        # maybe pre checkout

        # validate options
        self.__dry_run = config.get('dry_run', False)

        self.system = str.lower(platform.system())

        self.__start = config.get('start', None)
        self.__end = config.get('end', None)
        self.__only = config.get('only', None)

        self.__build_docs = config.get('build_docs', False)
        self.__chatty = config.get('chatty', False)
        self.__clean = config.get('clean', False)
        self.__devel = config.get('devel', False)
        self.__debug = config.get('debug', False)
        self.__skip_libcheck = config.get('skip_libcheck', False)
        self.__debuginfo = config.get('debuginfo', False)
        self.__release = config.get('release', False)
        self.__skip_unit = config.get('skip_unit', False)
        self.__static = config.get('static', False)
        self.__make_dash_j = int(config.get('j', 0))
        self.__target_only = config.get('target_only', None)

        bits = config.get('bits', None)
        if bits:
            self.bits = int(bits)
        else:
            self.bits = self.sys_bits

        self.compiler = config.get('compiler', None)
        self.test_config = config.get('test_config', '-')
        if not self.test_config:
            self.test_config = '-'
        self.use_ccache = config.get('use_ccache', False)
        self.tmpl_engine = config.get('tmpl_engine', 'jinja2')
        self.__write_codec = config.get('write_codec', None)
        self.__codec = None

        # TODO move out of init
        if not config.get('skip_env_check', False):
            if "LD_LIBRARY_PATH" in os.environ:
                raise Exception("environment variable LD_LIBRARY_PATH is set")

        self.check_config()

    def check_config(self):
        """
        called after config was modified to sanity check
        raises on error
        """

        # sanity checks - no config access past here
        if not getattr(self, 'stages', None):
            raise NotImplementedError("member variable 'stages' must be defined")
        # start at stage
        if self.__start:
            self.__stage_start = self.find_stage(self.__start)
        else:
            self.__stage_start = 0
        # end at stage
        if self.__end:
            self.__stage_end = self.find_stage(self.__end) + 1
            self.opt_end = self.__end
        else:
            self.__stage_end = len(self.stages)
        # only stage
        if self.__only:
            if self.__start or self.__end:
                raise Exception(
                    "stage option 'only' cannot be used with start or end")
            self.__stage_start = self.find_stage(self.__only)
            self.__stage_end = self.__stage_start + 1

        if self.__devel:
            self.__devel = True
            # force deploy skip
            if self.__stage_end >= len(self.stages):
                self.status_msg("removing deploy stage for development build")
# XXX                self.__stage_end = self.__stage_end - 1


        if self.stage_start >= self.stage_end:
            raise Exception("start and end produce no stages")

        if self.bits not in [32, 64]:
            raise Exception(
                "can't do a %d bit build: unknown build process" % self.bits)

        if self.bits == 64 and not self.is_64b:
            raise Exception(
                "this machine is not 64 bit, cannot perform 64 bit build")

        if self.system == 'windows':
            self.compilertag = 'vc10'
        elif self.system == 'linux':
            self.compilertag = 'gcc44'
        else:
            raise RuntimeError("can't decide compilertag on " + self.system)

        self.build_suffix = ''
        if not self.is_unixy:
            if self.__static:
                runtime = 'MT'
            else:
                runtime = 'MD'
            if self.__release:
                self.configuration_name = 'Release'
            else:
                runtime += 'd'
                self.configuration_name = 'Debug'

            self.build_suffix = '-' + runtime
            self.runtime = runtime
        else:
            self.configuration_name = 'CFNAME_INVALID_ON_LINUX'
            self.runtime = 'RUNTIME_INVALID_ON_LINUX'

        if self.test_config != '-':
            self.test_config = os.path.abspath(self.test_config)

        # split version
        if self.version:
            ver = self.version.split('.')
            self.version_major = int(ver[0])
            self.version_minor = int(ver[1])
            self.version_patch = int(ver[2])
            if(len(ver) == 4):
                self.version_build = int(ver[3])

    def check_definition(self):
        """
        called after Defintion was loaded to sanity check
        raises on error
        """
        if not self.write_codec:
            self.__write_codec = self.defined.data_ext

        # TODO need to add back a class scope target limited for subprojects with sub target sets
        targets = self.get_defined_targets()
        if self.__target_only:
            if self.__target_only not in targets:
                raise RuntimeError("invalid target '%s'" % self.__target_only)

            self.targets = [self.__target_only]
        else:
            self.targets = targets


    def _init_dirs(self):
        # define variables
        # top level

        # need changes
        #   name
        #   top_dir
        #   version
        #   release_environment

        # - build
        # is_devel
        # system
        # bits
        # build suffix
        # compiler tag


        ver_release_environment = os.path.join(self.version, self.release_environment)
        self.build_dir = os.path.join(
            self.top_build_dir, ver_release_environment, self.name)
        self.release_dir = os.path.join(
            self.top_release_dir, ver_release_environment, self.name)
        self.deploy_dir = os.path.join(self.release_dir, "_DEPLOY_")

        self.state_dir = os.path.join(self.top_state_dir, self.release_environment)

        self.fq_name = "%s-%s-%s" % (self.name, self.system, self.version)
        if self.is_devel:
            self.fq_name = self.fq_name + "-dev"
        self.fq_name += ("-%dbit" % self.bits) + self.build_suffix

        self.fq_release_name = '%s-%s' % (self.name, self.build_name)

        self.build_dirname = 'build-%dbit-%s%s' % (self.bits, self.compilertag, self.build_suffix)

        self.fq_build_dir = os.path.join(self.build_dir, self.fq_name)

    def _make_outdirs(self):
        self.mkdir(self.state_dir)
        self.mkdir(self.top_src_dir)
        self.mkdir(self.build_dir)
        self.mkdir(self.release_dir)

    def _check_attr(self, key):
        if not getattr(self, key, None):
            raise NotImplementedError(key + ' is required')

    def find_stage(self, stage):
        try:
            return self.stages.index(stage)
        except ValueError:
            raise ValueError("stage '%s' does not exist" % stage)

    def sanity_check(self):
        self._check_attr('name')
        self._check_attr('release_environment')

    ##########################################################################

    def find_datafile(self, name, search_path=None):
        """
        find all matching data files in search_path
        returns array of tuples (codec_object, filename)
        """
        if not search_path:
            search_path = self.define_dir

        return codec.find_datafile(name, search_path)

    def load_datafile(self, name, search_path=None, **kwargs):
        """
        find datafile and load them from codec
        """
        if not search_path:
            search_path = self.define_dir

        self.debug_msg('loading datafile %s from %s' % (name, str(search_path)))
        return codec.load_datafile(name, search_path, **kwargs)

    def find_define_dir(self):
		# FIXME - replace with find_initial util func
        return os.path.join(self.src_dir, 'config', 'facsimile')
        for name in ('facsimile', 'config'):
            define_dir = os.path.join(self.src_dir, name)
            if os.path.exists(define_dir):
#                if self.find_datafile('facsimile', define_dir):
                return define_dir

        return None

    ##########################################################################

    @property
    def defined(self):
        if not hasattr(self, 'defined__lazy'):
            self.debug_msg('creating definition, cwd=%s' % os.getcwd())
            self.defined__lazy = Definition(self)
            self.check_definition()
        return self.defined__lazy

    @property
    def state(self):
        if not hasattr(self, 'instance__lazy'):
            self.instance__lazy = State(self)
            self.debug_msg('creating instance, cwd=%s' % os.getcwd())
        return self.instance__lazy

    def get_defined_targets(self):
        cf = self.defined["deploy"]
        if "nodes" not in cf:
            return [cf["destdir"]]
        return cf['nodes'].keys()

    def deployment_set(self, target):
        if not isinstance(target, list):
            target = [target]

        cf = self.defined["deploy"]
        if "nodes" not in cf:
            return [cf["destdir"]]
        return set(reduce(lambda a, b: a + b, [cf["nodes"][t] for t in target]))

    def shell_list(self, target):
        cf = self.defined["deploy"]
        if "nodes" not in cf:
            return self.deployment_set(target)
        return ['%s@%s' % (cf['user'], m) for m in self.deployment_set(target)]

    def deploy_to(self, target):
        cf = self.defined["deploy"]
        dst_dir = self.defined['home']

        if not isinstance(target, list):
            target = [target]

        postcmd = self._deploy_postcmd(self.defined['deploy'])

        # sync files
        if "nodes" in self.defined["deploy"]:
            dst = "%s@%%s:%s/" % (cf["user"], dst_dir)
            #opts = ["--delete", "-e", "ssh"]
            opts = ["-e", "ssh -c blowfish"]

            for node in self.deployment_set(target):
                self._deploy_rsync(self.deploy_dir + "/", dst % node, opts)
                if postcmd:
                    self.call(["ssh", "%s@%s" % (cf["user"], node), postcmd])

        else:
            self._deploy_rsync(self.deploy_dir + "/", dst_dir)
            if postcmd:
                self.call(postcmd)

    def _deploy_postcmd(self, deploy):
        return ';'.join(deploy.get('postcmd', []))

    def _deploy_rsync(self, src, dst, opts=None):
        opts = list(opts)
        self.rsync(src, dst, opts)

        # check for self.name in deploy dir and do a second rsync with --delete
        # not ideal, but fixes cruft issues and is faster than rsync each dirwalk`x
        self_dir = os.path.join(src, self.name)
        if os.path.isdir(self_dir):
            opts.append('--delete')
            self.rsync(self_dir + '/', os.path.join(dst, self.name), opts)

    def libcheck_to(self, target):
        if self.skip_libcheck:
            print 'WARNING: skipped libcheck stage due to use of --skip-libcheck.'
            return

        fc = FileCompare(self)

        rv, out, err = self.call_get_output(
            [
                'sh', '-c', 'find %s -type f|grep -v "/\.debug/"|xargs -L1 file|grep "ELF %d"|grep "LSB executable"|cut -f1 -d:' %
                (self.deploy_dir, self.bits)])
        if rv or err:
            raise RuntimeError(
                "could not find LSB executables. rv %d err %s" % (rv, err))

        local_files = []
        for fn in out.split("\n"):
            if os.path.exists(fn):
                local_files.append(fn)

        for lbin in local_files:
            rv, out, err = self.call_get_output(['ldd', lbin])

            if rv or err:
                raise RuntimeError(
                    "could not LDD local executable %s. rv %d err %s" % (lbin, rv, err))

            for lddline in out.split("\n"):
                if lddline:
                    tokens = reduce(
                        lambda a, b: a + b, [tk.split(' ') for tk in lddline.split('\t')])
                    for tk in tokens:
                        if tk.startswith('/'):
                            fc.add_file(tk)

        cf = self.defined["deploy"]

        if not isinstance(target, list):
            target = [target]

        nodes_failed = list()

        if "nodes" in self.defined["deploy"]:
            user = cf["user"]

            n2t = {}
            for t in target:
                for node in cf["nodes"][t]:
                    n2t.setdefault(node, list())
                    n2t[node].append(t)

            for node in set(reduce(lambda a, b: a + b, [cf["nodes"][t] for t in target])):
                if not fc.check(n2t[node], user, node):
                    nodes_failed.append(node)

            if nodes_failed:
                raise Exception(
                    "Failed libcheck on node(s) %s. Aborting." % (', '.join(nodes_failed)))
        else:
            print 'skipping libcheck, on local machine.'

    ##########################################################################

    def alact(self, phrase):
        return False
        try:
            return subprocess.call(['alact', phrase]) == 0
        except OSError:
            return False

    # FIXME - codec_load codec is a class, write_codec is an ext, both fail due to loading order
    @property
    def codec(self):
        if not self.__codec:
            cls = codec.get_codec(self.defined.data_ext)
            if cls:
                self.__codec = cls()
        return self.__codec

    @property
    def write_codec(self):
	if self.__write_codec:
	    return self.__write_codec
	return self.codec

    @property
    def chatty(self):
        if self.__chatty:
            return True
        if hasattr(self, 'opt_end'):
            return False
        return bool(self.release_environment in ('production', 'vip0'))

    @property
    def destdir(self):
        return self.defined['deploy']['destdir']

    @property
    def is_local(self):
        return not "nodes" in self.defined["deploy"]

    def list_nodes(self):
        return self.defined["deploy"]["nodes"].items()

    def print_summary(self):
        print "Summary"
        #print "home ", self.defined['home']

        for attr in self.summary_attrs:
            print "%s: %s" % (attr, str(getattr(self, attr, None)))

        print "version=%s instance=%s" % (self.version, self.release_environment)
        return 0

    def print_list_codecs(self):
        print codec.list_codecs()
        return 0

    def print_list_nodes(self):
        try:
            print '\nNodes that this instance uses:'
            for node, nodes in self.list_nodes():
                print '%s:' % node
                for n in nodes:
                    print '  %s' % n
        except KeyError:
            print 'cannot determine nodes, you are probably doing a localhost push.'

        return 0

    def run(self):
        """ run all configured stages """

        self.sanity_check()

# TODO - check for devel
#        if not self.version:
#            raise Exception("no version")
# XXX check attr exist
        if not self.release_environment:
            raise Exception("no instance name")

        time_start = time.time()

        cwd = os.getcwd()

        who = getpass.getuser()
        self._make_outdirs()

        append_notices = ""
        if hasattr(self, 'opt_end'):
            append_notices = ". shortened push, only to %s stage" % self.opt_end
        if self.is_devel:
            append_notices += ". devel build"
        if hasattr(self, 'append_notices'):
            append_notices += self.append_notices

        line = "%s %s %s by %s%s" % (
            sys.argv[0], self.version, self.release_environment, who, append_notices)
        b = 'deploy begin %s' % line
        e = 'deploy done %s' % line

        if self.chatty:
            self.alact(b)

        ok = False
        stage_passed = None
        try:
            for stage in self.stages[self.stage_start:self.stage_end]:
                self.debug_msg("stage %s starting" % (stage,))
                getattr(self, stage)()
                self.chdir(cwd)
                stage_passed = stage
                self.debug_msg("stage %s complete" % (stage,))
            ok = True
        finally:
            if not ok:
                if self.chatty:
                    if not stage_passed:
                        self.alact(
                            'deploy failed %s. completed no stages' % line)
                    else:
                        self.alact('deploy failed %s. completed %s' %
                                   (line, stage_passed))
        self.status_msg('[OK]')
        if self.chatty:
            self.alact('%s in %0.3f sec' % (e, time.time() - time_start))

        return 0

    def status_msg(self, msg):
        print ": " + msg

    def debug_msg(self, msg):
        print "# " + msg

    def cmd_msg(self, msg):
        print "+ " + msg

    def chdir(self, *args):
        name = os.path.join(*args)

        if self.__dry_run:
            self.cmd_msg("cd " + name)
            return

        if self.__debug:
            self.cmd_msg("cd " + name)
        os.chdir(name)

    def mkdir(self, *args):
        name = os.path.join(*args)

        if self.__dry_run:
            self.cmd_msg("mkdir " + name)
            return

        if self.__debug:
            self.cmd_msg("mkdir " + name)

        if not os.path.exists(name):
            os.makedirs(name)

    def rmdir(self, *args):
        name = os.path.join(*args)

        if self.__dry_run:
            print "+ rmdir " + name
            return

        if self.__debug:
            self.cmd_msg("rmdir " + name)

        if os.path.exists(name):
            shutil.rmtree(name)

    def cp(self, src, dst):
        if self.__dry_run:
            self.cmd_msg("cp %s %s" % (src, dst))
            return

        if self.__debug:
            self.cmd_msg("cp %s %s" % (src, dst))

        try:
            os.makedirs(os.path.dirname(dst))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

        shutil.copy2(src, dst)

    def cp_r(self, src, dst):
        if self.__dry_run:
            self.cmd_msg("cp -r %s %s" % (src, dst))
            return

        if self.__debug:
            self.cmd_msg("cp -r %s %s" % (src, dst))

        # should probably take the dir name from src and append to dst so it's
        # "normal" syntax
        shutil.copytree(src, dst)

    def mv(self, src, dst):
        if self.__dry_run:
            self.cmd_msg("mv %s %s" % (src, dst))
            return

        if self.__debug:
            self.cmd_msg("mv %s %s" % (src, dst))

        shutil.move(src, dst)

    ##########################################################################

    def call(self, args, read="", write=""):
        if not args:
            raise ValueError('call passed no arguments')

        if isinstance(args, str):
            args = shlex.split(args)

        if self.dry_run:
            self.cmd_msg(" ".join(args))
            return

        if self.is_debug:
            self.cmd_msg(" ".join(args))

        rv = 0
        if len(write):
            p = subprocess.Popen(args, stdin=subprocess.PIPE)
            p.stdin.write(write)
            p.stdin.close()
            p.communicate()
            rv = p.returncode
        else:
            rv = subprocess.call(args)

        if rv != 0:
            raise RuntimeError("process %s returned %d %s" %
                            (args[0], rv, str(args)))

    def call_get_output(self, args, bufsize=16777216):
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        rv = p.returncode
        return rv, out, err

    def run_cmd(self, cmd):
        if self.dry_run:
            self.cmd_msg(cmd)
            return

        if self.is_debug:
            self.cmd_msg(cmd)

        status = os.system(cmd)
        if status > 0:
            raise RuntimeError("command `%s` failed with exit code %d pwd=%s" % (cmd, status, os.getcwd()))

    def write_sasldb(self, filename):
        cmd = ["/usr/sbin/saslpasswd2", "-c",
               "-p", "-f", filename, "-u", "QPID"]
        for k, v in self.state.passwd().items():
            args = cmd[:]
            args.append(k)
            self.call(args, write=v)

    def write_dhseed(self, filename):
        self.call("openssl dhparam -out " + filename + " 2048")

    def write_version(self, filename=None):
        if not filename:
            dir = os.path.join(self.deploy_dir, "etc")
            print "mkdir ", dir
            self.mkdir(dir)
            filename = os.path.join(dir, self.name + ".version")

        f = open(filename, "w")
        f.write(self.version + "\n")
        f.close()

    def make_virtualenv(self, name=None, req_file=None, src_dir=None):
        if not name:
            name = self.name
        if not src_dir:
            src_dir = self.src_dir

        env_dir = os.path.join(self.fq_build_dir, name)
        self.debug_msg("making virtualenv %s" % env_dir)

        if os.path.exists(env_dir) and not self.clean:
            return

        if not os.path.exists(src_dir):
            raise IOError("src_dir '%s' does not exist" % (src_dir,))

        # force dir rm, since virtual env won't redo links
        self.rmdir(env_dir)
        args = [
            os.path.join(self.script_dir, "make_virtualenv.sh"),
            src_dir,
            env_dir
        ]
        if req_file:
            args.append(req_file)

        # FIXME broken with addition of requirements file, move to environ
        #if self.use_ccache:
        #    args.append("USE_CCACHE")
        try:
            self.call(args)

        except:
            self.rmdir(env_dir)
            raise

    def copy_virtualenv(self, name=None):
        if not name:
            name = self.name

        env_dir = os.path.join(self.fq_build_dir, name)

        args = [
            os.path.join(self.script_dir, "copy_virtualenv.sh"),
            env_dir,
            self.deploy_dir,
            os.path.join(self.defined['home'], name)
        ]
        self.call(args)

    def rsync(self, src, dst, opts=[]):
        # --size-only for py tree
        self.debug_msg('syncing to %s' % dst)
        args = ["rsync", "-aLp"]

        exclude_file = os.path.join(self.define_dir, "exclude.rsync")
        if os.path.exists(exclude_file):
            args.extend(["--exclude-from", exclude_file])

        args.extend(opts)

        args.append(src)
        args.append(dst)
        self.call(args)

    def git_checkout(self, src, dst=None, tag=None):
        if self.__nocheckout:
            return
        if not dst:
            dst = self.src_dir
        if not tag and not self.__devel:
            tag = self.version
        ocwd = os.getcwd()

        if os.path.exists(dst):
            # no tag is devel, update and return
            if not tag:
                os.chdir(dst)
                self.run_cmd("git pull")
                self._git_checkout_submodules()
                return

            # release tags should never change
            if not self.clean:
                return

            self.rmdir(dst)

        if os.path.exists(dst):
            raise RuntimeError("did not expect %s to exist" % dst)

        success = False
        try:
            # print 'about to clone - ocwd %s src %s dst %s' % (ocwd, src, dst)

            self.run_cmd("git clone %s '%s'" % (src, dst))
            os.chdir(dst)
            # invalid tag results in git erroring and script stopping from
            # exception
            if tag:
                self.run_cmd("git checkout " + tag)
            self._git_checkout_submodules()
            success = True
        finally:
            if not success:
                # invalid tag or other git problem results in git erroring and script stopping from exception
                # we also should clean up the directory, as otherwise we will leave it to screw up future executions
                # of this script, it's important not to leave a master checkout
                # there for instance
                if os.path.exists(dst):
                    print 'failed checkout checkout, removing %s as it was not properly checked out' % dst
                    shutil.rmtree(dst)

        os.chdir(ocwd)
        return success

    def _git_checkout_submodules(self):
        self.run_cmd("git submodule init")
        self.run_cmd("git submodule update")
        self.run_cmd("git submodule foreach git submodule init")
        self.run_cmd("git submodule foreach git submodule update")

    def tmpl_path(self, dirname):
        path = os.path.join(self.define_dir, dirname)
        rv = []
        for each in ('_ALL_', self.release_environment):
            subdir = os.path.join(path, each)
            if os.path.exists(subdir):
                rv.append(subdir)
        self.debug_msg("tmpl paths %s" % str(rv))
        return rv


class Facsimile(Base):
    """
    Generic Facimile definition
    """

    name = 'facsimile'

    stages = ["checkout", "build", "install", "deploy"]

    def checkout(self):
        if not hasattr(self, 'repo'):
            raise Exception("repo not defined")
        if isinstance(self.repo, str):
            self.debug_msg("checking out %s" % (self.repo,))
            self.git_checkout(self.repo)

        return True

        # ensure current is loaded
        self.defined._load()

        # check for checked out def file, switch define dir and load
        define_dir = os.path.join(self.src_dir, 'facsimile')
        if not self.find_datafile("facsimile", define_dir):
            return True

        self.define_dir = define_dir
        # load from new path
        self.defined._load()
        return True

    def build(self):
        pass

    def install(self):
        install = self.defined.get('install', None)
        if not install:
            return

        self.rmdir(self.deploy_dir)
        self.mkdir(self.deploy_dir)
#        pprint.pprint(self.state.tree())

        for grp in install['groups']:
            if grp.get('type', None) == 'tmpl':
                self._install._package_group(grp, self.release_dir)
            else:
                self._install._package_group(grp, self.deploy_dir)

        self.write_version()

        return True

    def deploy(self):
        self.status_msg("deploying...")
#        if not self.targets:
        self.deploy_to(self.targets)


class VirtualEnv(Facsimile):
    """
    virtualenv from repo
    expects requirements.txt in basedir
    """

    name = 'virtualenv'

    def build(self):
        self.status_msg("building...")
        self.make_virtualenv()

    def install(self):
        self.rmdir(self.deploy_dir)
        self.mkdir(self.deploy_dir)

        self.write_version()
        self.copy_virtualenv()
        return True


