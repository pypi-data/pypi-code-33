# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of xanity.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
"""
This is the central file of 'xanity'.
"""
import fnmatch
import tarfile
import gc
import os
import logging
import sys
import time
import traceback
import cProfile as profile
import datetime
import inspect
import subprocess

from pkg_resources import resource_filename
from bdb import BdbQuit
from shlex import split as shsplit

from .common import Status, Analysis, Experiment, Constants
from .common import XanityDeprecationError, XanityNoProjectRootError, XanityNotOrientedError, XanityUnknownActivityError
from .common import digest_file, digest_string, pickle_dump, pickle_load, file2mod, list_modules_at_path, get_arg_names
from .common import get_external_caller
from .constants import COMMANDS, RELATIVE_PATHS, ACTIVITIES, DIRNAMES, XANITY_FILES, INVOCATION
from .cli import parser

xanity_exe_path = resource_filename('xanity', '/bin')
if 'PATH' in os.environ:
    os.environ['PATH'] = xanity_exe_path + ':' + os.environ['PATH']
else:
    os.environ['PATH'] = xanity_exe_path

if sys.version_info.major == 2:
    import imp
    from codecs import open

    PY_SYSVER = 2

elif sys.version_info.major == 3:
    import importlib

    PY_SYSVER = 3


class ContextDecorator:
    def __init__(self, context):
        self.context = context

    def __call__(self, f):
        
        def f_wrapped(xanity, *args, **kwargs):

            if ACTIVITIES is not None and hasattr(ACTIVITIES, 'EXTERNAL') and self.context == ACTIVITIES.EXTERNAL:

                xanity._register_external_access(get_external_caller())

            with xanity.status.act_tags(self.context):

                result = f(xanity, *args, **kwargs)

            return result

        return f_wrapped


# class CheckpointManager(object):
#     def __init__(self, xanity, names, tvars=None):
#         self.names = names
#         self.vars = tvars
#         self.xanity = xanity
#
#     def __enter__(self):
#         res = self.xanity.load_checkpoint(self.names)
#         if all([r is not None for r in res]):
#             return Exit
#         else:
#             yield
#
#     def __exit__(exc_type, exc_val, exc_tb):


class Xanity(object):

    def __init__(self):
        self.status = Status()

        with self.status.act_tags(ACTIVITIES.CONSTRUCT):
            self.start_time = time.localtime()
            self.run_id = time.strftime('%Y-%m-%d-%H%M%S', self.start_time)
            self.project_root = None
            self._rcfile = None
            self._env_path = None
            self.name = ''
            self.paths = None
            self.conf_files = None
            # self.uuid = ''
            self.action = None
            self.invoker = None
            self.callers = set()
            self.importers = set()
            self._registered_associations = {}
            self._exps_requesting_analysis = set()
            self._exp_paramset_requests = {}
            self._trial_requests = {}
            self.invocation = None

            self.avail_experiments = {}
            self.avail_analyses = {}
            self._init_logger()
            self._oriented = False
            self._requests_resolved = False
            self._has_run = False

    @ContextDecorator(ACTIVITIES.DEL)
    def __del__(self):
        # destruction of the xanity obj will be the sole trigger of experiments and analyses
        print('(xanity exit)')

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_args(self, clargs=None):
        """ parse MODULE arguments """

        if self.invocation == INVOCATION.HOOK:
            if clargs is None:
                clargs = []

                if self.invoker is not None:
                    caller = self.invoker
                elif len(self.callers) == 1:
                    caller = list(self.callers)[0]
                else:
                    import ipdb
                    ipdb.set_trace()

                if caller in [exp.module_path for exp in self.avail_experiments.values()]:
                    clargs.extend([COMMANDS.RUN.name, file2mod(caller)])

                elif caller in [anal.module_path for anal in self.avail_analyses.values()]:
                    clargs.extend([COMMANDS.ANAL.name, '-a', file2mod(caller)])

            clargs.extend(sys.argv[1:])  # pickup any commandline args

        args, unknownargs = parser(self, clargs)

        if hasattr(args, 'action'):
            if args.action in COMMANDS:
                self.action = args.action
                self.args = args
                self.unknownargs = unknownargs
                
                if self.action == COMMANDS.RUN:
                    if self.args.checkpoints:
                        self.args.savecp = True
                        self.args.loadcp = True

            elif args.action in dir(self):
                self.action = args.action

            else:
                raise XanityUnknownActivityError

        else:
            raise XanityUnknownActivityError

        # else:
        #     print('\nunknown or missing xanity action')
        #     raise SystemExit(1)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_associations(self):
        """ parse requested action_objects and options"""
        if not self.project_root:
            raise XanityNoProjectRootError

        # first, resolve declared associations
        for anal, exps in self._registered_associations.items():
            # self._trip_hooks(anal, 'associated_experiments')
            self.avail_analyses[anal].experiments.update({exp: self.avail_experiments[exp] for exp in exps})
            [self.avail_experiments[exp].analyses.update({anal: self.avail_analyses[anal]}) for exp in exps]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _purge_dangling_experiments(self):
        # remove non-existant experiments from those analyses that were just added
        if self.action in COMMANDS.RUN:
            for anal in self.analyses.values():
                chop = []
                for exp in anal.experiments.values():
                    if exp.name not in self.experiments.keys():
                        chop.append(exp.name)
                for name in chop:
                    del anal.experiments[name]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_requests(self):
        """ parse requested action_objects and options"""
        if not self.project_root:
            raise XanityNoProjectRootError

        self.experiments = {}
        self.analyses = {}

        # if running, define experiments to run
        if self.action == COMMANDS.RUN:
            if hasattr(self.args, 'experiments') and self.args.experiments:
                expreqd = self.args.experiments
                print('looking for requested experiments: {}'.format(expreqd))

                if not all([item in self.avail_experiments for item in expreqd]):
                    print('couldnt find a requested experiment.')
                    raise SystemExit(1)

                self.experiments = {item: self.avail_experiments[item] for item in expreqd}

            else:
                if self.invocation == INVOCATION.HOOK:
                    cli_mods = [file2mod(fp) for fp in self.callers]
                    if any([climod in self.avail_experiments for climod in cli_mods]):
                        self.experiments = {item: self.avail_experiments[item] for item in cli_mods if
                                            item in self.avail_experiments}
                    else:
                        callmods = [file2mod(fp) for fp in self.callers]
                        if any([clmod in self.avail_experiments for clmod in callmods]):
                            self.experiments = {item: self.avail_experiments[item] for item in callmods if
                                                item in self.avail_experiments}
                else:
                    self.experiments = self.avail_experiments

            if self.args.and_analyze is not None:
                if self.args.and_analyze:
                    analreqd = self.args.and_analyze
                    assert all([item in self.avail_analyses for item in analreqd]), 'couldnt find a requested analysis'
                    self.analyses = {item: self.avail_analyses[item] for item in analreqd}
                else:
                    self.analyses = self.avail_analyses
            else:
                self.analyses = {}

        # if analyzing define anals to run
        elif self.action == COMMANDS.ANAL:

            if self.args.analyses:
                analreqd = self.args.analyses
                if not all([item in self.avail_analyses for item in analreqd]):
                    print('couldn\'t find a requested analysis')
                    raise SystemExit(1)
                self.analyses = {item: self.avail_analyses[item] for item in analreqd}
            else:
                self.analyses = self.avail_analyses

            if self.args.runid:
                anal_dirs = []
                for item in self.args.runid:
                    matches = self._resolve_data_path(item)
                    if not matches:
                        print('couldnt find a requested analysis.')
                        raise SystemExit(1)
                    anal_dirs.append(matches[-1])
                self.anal_data_dir = anal_dirs

            else:
                self.anal_data_dir = self._find_recent_run_path()
                if self.anal_data_dir is None:
                    print('')
                    raise SystemExit(1)
        else:
            self.experiments = {}
            self.analyses = {}

        if self.action == COMMANDS.RUN:
            # for those experiments requesting analysis, add analyses, if necessary

            # for exp in self.experiments.values():
            #     self._trip_hooks(exp, 'analyze_this')

            for exp in self._exps_requesting_analysis:
                if exp in self.experiments:
                    for anal, anal_it in self.avail_analyses.items():
                        if exp in anal_it.experiments:
                            self.experiments[exp].analyses.update({anal: anal_it})

        self._requests_resolved = True

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _process_parameters(self):
        """see if any experiments have asked for param-sets """

        if not self._oriented:
            raise XanityNotOrientedError

        # first, get all parameter hooks
        # for exp in self.experiments.values():
        #     self._trip_hooks(exp, 'experiment_parameters')

        self._parse_exp_params()

        for experiment in self.experiments.values():

            def create_single_subexp_dir():
                # create single subexperiment directory
                experiment.update({
                    'subexp_dirs': [os.path.join(self.exp_data_dir, experiment.name)],
                    'success': [False],
                    'paramsets': [experiment.default_params],
                })
        
            def create_multiple_subexp_dirs(number):
                # create multiple
                experiment.update({
                    'subexp_dirs': [os.path.join(self.exp_data_dir, experiment.name, '{}_{}'.format(experiment.name, i))
                                    for i in range(number)],
                    'success': [False] * number,
                    'paramsets': [experiment.default_params] * number,
                })
            
            if experiment.name in self._exp_paramset_requests:
                experiment.param_dict = self._exp_paramset_requests[experiment.name]

                for key, value in experiment.param_dict.items():
                    if type(value) is not list:
                        experiment.param_dict[key] = [value]

                # get number of subexperiments
                frozen_names = tuple(experiment.param_dict.keys())
                kwlens = [len(experiment.param_dict[name]) for name in frozen_names]
                indmax = [item - 1 for item in kwlens]

                # compose all parameter sets
                indvec = [[0] * len(kwlens)]
                while True:
                    tvec = list(indvec[-1])
                    if tvec == indmax:
                        break
                    tvec[-1] += 1
                    for place in reversed(range(len(kwlens))):
                        if tvec[place] > indmax[place]:
                            if place == 0:
                                break
                            else:
                                tvec[place - 1] += 1
                                tvec[place] = 0

                    indvec.append(tvec)
                    if indvec[-1] == indmax:
                        break

                # store all parameter sets
                # create all the subexperiment info
                create_multiple_subexp_dirs(len(indvec))
                experiment.update({
                    'paramsets': [{frozen_names[i]: experiment.param_dict[frozen_names[i]][choice] for i, choice in
                                   enumerate(vect)} for vect in indvec],
                })

            elif experiment.name in self._trial_requests and self._trial_requests[experiment.name]>1:
                
                # create all the subexperiment info
                create_multiple_subexp_dirs(self._trial_requests[experiment.name])
                    
    
            else:
                # create single subexperiment directory
                create_single_subexp_dir()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_anal_data(self):
        """ unsure... """
        if self.experiments and self.action == COMMANDS.RUN:
            for anal in self.analyses.values():
                rm = []
                for exp in anal.experiments.values():
                    if all([not item for item in exp.success]):
                        rm.append(exp.name)
                for name in rm:
                    del anal.experiments[name]

        elif self.analyses and self.action == COMMANDS.ANAL:
            for anal in self.analyses.values():
                rm = []
                for exp in anal.experiments.values():
                    if not any([exp.name in os.listdir(d) for d in self.anal_data_dir]):
                        rm.append(exp.name)
                for name in rm:
                    del anal.experiments[name]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _init_logger(self):
        """ setup a logger ... """
        # create logger
        self.logger = logging.getLogger('xanity_logger')
        self.logger.handlers = []
        self.logger.setLevel(logging.DEBUG)

        # lsh = logging.StreamHandler(sys.stdout)
        # lsh.setFormatter(logging.Formatter(self.exp_data_dir.split('/')[-1] + ' %(asctime)s :%(levelname)s: %(message)s'))
        # lsh.setLevel(logging.DEBUG)
        # self.logger.addHandler(lsh)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _attach_root_logger_fh(self):
        lfh = logging.FileHandler(filename=os.path.join(self.exp_data_dir, 'root.xanity.log'))
        lfh.setFormatter(logging.Formatter('%(asctime)s :%(levelname)s: %(message)s'))
        lfh.setLevel(logging.DEBUG)
        self.logger.addHandler(lfh)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_exp_params(self):
        """ get default parameters """
        malformed = []
        for experiment in self.experiments.values():
            # sig = _get_mainfn_sig(os.path.join(self.paths.experiments, experiment + '.py'))
            if not hasattr(experiment.module, 'main'):
                malformed.append(experiment.name)
            else:
                if PY_SYSVER == 3:
                    sig = inspect.signature(experiment.module.main)
                    experiment.default_params = {parameter.name: parameter.default for parameter in
                                                 sig.parameters.values()}
                elif PY_SYSVER == 2:
                    sig = inspect.getargspec(experiment.module.main)
                    experiment.default_params = {parameter: sig.defaults[i]
                                                 for i, parameter in enumerate(sig.args)}
        for exp in malformed:
            if exp in self.avail_experiments:
                del self.avail_experiments[exp]
            if exp in self.experiments:
                del self.experiments[exp]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _load_required_modules(self):
        """
        docstring
        :return:
        """

        sys.path.append(self.paths.experiments)
        for name, fullpath in [(exp.name, exp.module_path) for exp in self.experiments.values()]:
            self.experiments[name].module = self._get_live_module(fullpath)
        sys.path.remove(self.paths.experiments)

        sys.path.append(self.paths.analyses)
        for name, fullpath in [(anal.name, anal.module_path) for anal in self.analyses.values()]:
            self.analyses[name].module = self._get_live_module(fullpath)
        sys.path.remove(self.paths.analyses)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_avail_modules(self):
        """
        docstring
        :return:
        """
        # self.exp_package = _get_live_package_object(self.paths.experiments)
        # self.anal_package = _get_live_package_object(self.paths.analyses)
        # sys.modules['experiments'] = self.exp_package
        # sys.modules['analyses'] = self.anal_package

        exp_list = self._list_avail_experiments()
        anal_list = self._list_avail_analyses()

        sys.path.append(self.paths.experiments)
        for name, fullpath in exp_list:
            # self.avail_experiments.update({name: Experiment(name, fullpath, importlib.import_module('experiments.'+name))})
            self.avail_experiments.update({name: Experiment(name, fullpath, None)})
        sys.path.remove(self.paths.experiments)

        sys.path.append(self.paths.analyses)
        for name, fullpath in anal_list:
            # self.avail_analyses.update({name: Analysis(name, fullpath, importlib.import_module('analyses.'+name))})
            self.avail_analyses.update({name: Analysis(name, fullpath, None)})
        sys.path.remove(self.paths.analyses)

    @ContextDecorator(ACTIVITIES.ORIENT)
    def _orient(self, clargs=None):
        """
        just-in-time orientation
        :param clargs:
        :return:
        """

        # sensitive ordering
        if not self.project_root:
            self._resolve_xanity_root()

        if self.action is not None and clargs is not None:
            raise XanityUnknownActivityError

        if self.action is None:
            self._parse_args(clargs)

        if self.action in COMMANDS.RUN:
            rundir_sig = '{}-debug' if self.args.debug else '{}'
            self.exp_data_dir = os.path.join(self.paths.run_data,
                                          rundir_sig.format(self.run_id))
            self.anal_data_dir = self.exp_data_dir

        self._oriented = True

    @ContextDecorator(ACTIVITIES.MOD_LOAD)
    def _get_live_module(self, module_path):
        # module_dir = os.path.split(module_path)[0]
        # opwd = os.getcwd()
        # os.chdir(module_dir)
        if self.paths.experiments in module_path:
            sys.path.append(self.paths.experiments)
        elif self.paths.analyses in module_path:
            sys.path.append(self.paths.analyses)

        module_name = file2mod(module_path)
        if PY_SYSVER == 2:
            module = imp.load_source(module_name, module_path)
        else:
            spec = importlib.util.spec_from_file_location(module_name, location=module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _condabashcmd(self, cmd):
        return shsplit('bash --rcfile {} -ic \'{}\''.format(self.conf_files.rcfile, cmd))

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _save_conda_snapshot(self):
        if not self.args.debug:
            with open(os.path.join(self.exp_data_dir, 'conda_env_state'), 'w') as f:
                f.write(
                    subprocess.check_output(self._condabashcmd('conda list'), stderr=subprocess.PIPE).decode()
                )

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _archive_source_tree(self):
        if not self.args.debug:

            ignore = [
                '/data/runs',
                '/data/saved',
                '/.xanity',
                '/.git',
                ]

            # make requirements.txt
            reqs = subprocess.check_output(['pip', 'freeze']).decode()
            with open(os.path.join(self.exp_data_dir, 'requirements.txt'), mode='w') as reqsfile:
                for line in reqs:
                    reqsfile.write(line + '\n')

            filterfn = lambda tarinfo: None if any([pattern in tarinfo.name for pattern in ignore])\
                else tarinfo

            with tarfile.open(os.path.join(self.exp_data_dir, 'source.tar.gz'), mode='w:gz') as tarball:
                tarball.add(self.project_root, arcname=self.name + '--' + self.run_id, filter=filterfn)

            ## dump tarballs of source
            # if os.path.isdir(os.path.join(data_dir, 'src')):
            #    tarball = tarfile.open(os.path.join(self.exp_data_dir, 'src.tar.gz'), mode='w:gz')
            #    tarball.add(src_dir, arcname='src')
            #    tarball.close()

            ## dump tarballs of libraries
            # if os.path.isdir(os.path.join(data_dir, 'lib')):
            #    tarball = tarfile.open(os.path.join(self.exp_data_dir, 'lib.tar.gz'), mode='w:gz')
            #    tarball.add(xanity_root + '/lib', arcname='lib')
            #    tarball.close()

            ## dump tarballs of includes
            # if os.path.isdir(os.path.join(data_dir, 'inc')):
            #    tarball = tarfile.open(os.path.join(self.exp_data_dir, 'include.tar.gz'), mode='w:gz')
            #    tarball.add(xanity_root + '/include', arcname='include')
            #    tarball.close()

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def find_data(self, experiment_name):
        return os.path.join(self._find_recent_run_path(experiment_name), experiment_name)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _find_recent_run_path(self, experiment_names=None):
        if experiment_names is None:
            expnames = set()
            for anal in self.analyses.values():
                expnames.update([exp.name for exp in anal.experiments.values()])

        else:
            expnames = experiment_names if not isinstance(experiment_names, str) else [experiment_names]

        cands = []

        rcands = []
        for dirs, subdirs, files in os.walk(self.paths.run_data, followlinks=False):
            if any([subdir in expnames for subdir in subdirs]):
                rcands.append(dirs)

        cands.extend(sorted(set(rcands), key=str.lower))

        rcands = []
        for dirs, subdirs, files in os.walk(self.paths.saved_data, followlinks=False):
            if any([subdir in expnames for subdir in subdirs]):
                rcands.append(dirs)

        cands.extend(sorted(set(rcands), key=str.lower))

        if len(cands) > 0:
            print(cands)
            return cands[-1]
        else:
            print('could not find any recent data to analyze')
            return None

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_data_path(self, pathstring):
        run_matches = fnmatch.filter(os.listdir(self.paths.run_data), pathstring + '*')
        save_matches = fnmatch.filter(os.listdir(self.paths.saved_data), pathstring + '*')

        if run_matches or save_matches:
            matches = [os.path.join(self.paths.run_data, match) for match in run_matches] \
                    + [os.path.join(self.paths.saved_data, match) for match in save_matches]
            matches.sort()
            return matches
        else:
            raise IOError('\m couldn\'t resolve requested data-dir for analysis')

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _in_xanity_tree(self, file_or_path=None):
        """returns the root of a xanity tree

        test a file/dir to see if it's in a xanity tree.

        :param file_or_path: hint for searching

        :returns: root of hinted xanity project tree
        """
        result = None

        if not file_or_path:
            file_or_path = os.getcwd()

        else:
            if os.path.isfile(file_or_path):
                file_or_path = os.path.split(file_or_path)[0]
            elif os.path.isdir(file_or_path):
                pass
            else:
                file_or_path = os.getcwd()

        path_parts = file_or_path.split('/')

        for i in range(len(path_parts))[::-1]:
            test_path = '/' + os.path.join(*path_parts[:i + 1])
            if os.path.isdir(os.path.join(test_path, '.xanity')):
                result = test_path
                break

        return result

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_xanity_root(self):
        """attempts to ground the current xanity within a tree

                look at given disposition and determine a xanity root

                """
        result = self._in_xanity_tree()

        if not result:
            print('not presently within a xanity tree')

            # look into 'callers' first, then 'importers' for hints
            cands = set(filter(lambda item: bool(item), [self._in_xanity_tree(hint) for hint in self.callers]))
            if len(cands) > 1:
                print('multiple xanity project roots found... usure what to do')
                raise NotImplementedError
            if len(cands) == 1:
                result = cands.pop()

            if not result:
                # now try importers
                cands = set(filter(lambda item: bool(item), [self._in_xanity_tree(hint) for hint in self.importers]))
                if len(cands) > 1:
                    print('multiple xanity project roots found... usure what to do')
                    raise NotImplementedError
                if len(cands) == 1:
                    result = cands.pop()

                if not result:
                    print('coudn\'t find a relevant xanity project root.  exiting.')
                    raise XanityNoProjectRootError

        self._populate_root_info(result)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _populate_root_info(self, root_path):
        if os.path.isdir(os.path.join(root_path, '.xanity')):
            self.project_root = root_path
            self.name = self.project_root.split('/')[-1]
            self.paths = Constants({
                key: os.path.join(self.project_root, value)
                for key, value in RELATIVE_PATHS.items()})
            self.conf_files = Constants({
                key: os.path.join(self.project_root, value)
                for key, value in XANITY_FILES.items()})
            self._rcfile = self.conf_files['rcfile']
            self._env_path = self.conf_files['conda_env']
            # self.uuid = open(self.conf_files.uuid, mode='r').read().strip()
            self._parse_avail_modules()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _register_import(self, caller):
        if caller not in self.callers:
            # self._check_invocation()
            self.importers.add(caller)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _register_external_access(self, caller):
        if caller not in self.callers:
            # self._check_invocation()
            self.callers.add(caller)

    # @ContextDecorator(ACTIVITIES.INTERNAL)
    # def _resolve_action_from_hook(self):
    #     if not self.invocation == INVOCATION.HOOK:
    #         return
    #
    #     votes = []
    #
    #     def sortit(filepath, votes):
    #         caller_name = file2mod(filepath)
    #         if caller_name in self.avail_experiments:
    #             votes.append(COMMANDS.RUN)
    #         elif caller_name in self.avail_analyses:
    #             votes.append(COMMANDS.ANAL)
    #
    #     for caller in self.callers:
    #         sortit(caller, votes)
    #
    #     if COMMANDS.RUN in votes:
    #         return COMMANDS.RUN
    #
    #     elif COMMANDS.ANAL in votes:
    #         return COMMANDS.ANAL
    #     else:
    #         return None

    # @ContextDecorator(ACTIVITIES.INTERNAL)
    # def _check_invocation(self):
    #
    #     invocation = ' '.join(sys.argv)
    #
    #     if invocation.startswith('-m '):
    #         # looks like an import... no useful arguments in sys.argv
    #         self.invocation = INVOCATION.IMPORT
    #         print('import only...')
    #
    #     elif '/xanity/__main__.py ' in invocation or invocation.startswith('xanity'):
    #         # invoked directly -- arg parser will catch everything
    #         self.invocation = INVOCATION.COMMAND
    #         print('called directly')
    #
    #     else:
    #         # started from an import or a hook
    #         # root = self.resolve_xanity_root()
    #
    #         matcher = re.compile(r'((?:[\\/]?\w+)+.py)')
    #         self.invocation_files = matcher.findall(invocation)
    #         self.invocation = INVOCATION.HOOK
    #         print('called from hook')
    #         # if not root:
    #         #     for tfile in self.invocation_files:
    #         #         root = self.resolve_xanity_root(tfile)
    #         #         if root:
    #         #             break
    #         #
    #         # else:
    #         #     self.project_root = root
    #         #     self.called_from_hook = True   # deprecated
    #         #     print('run hook from file')
    #
    #     self._parse_args()

    @ContextDecorator(ACTIVITIES.RUN)
    def _absolute_trigger(self):
        """
        docstring
        :return:
        """
        if not self._oriented:
            raise XanityNotOrientedError

        self._resolve_requests()
        self._purge_dangling_experiments()
        self._load_required_modules()
        self._resolve_associations()
        self._process_parameters()

        self.n_total_exps = sum([len(item.success) for item in self.experiments.values()])
        self.n_total_anals = sum([len(item.experiments) for item in self.analyses.values()])

        if not self._check_environment():
            print('\n\n'
                  'looks like you\'re not inside the correct conda environment. \n'
                  'If you\'re using an IDE or calling a script directly, \n'
                  'please be sure you\'re using the python inside the \n'
                  'conda environment at path:\n{}\n\n'.format(self.conf_files.conda_env))
            raise SystemExit(1)
        # if not self.check_conda():
        #     print('\n\n'
        #           'looks like you\'ve made some changes '
        #           'to your conda environment file....\n'
        #           'please issue \'xanity setup\' to resolve the new one')
        #     raise SystemExit(1)

        self._check_xanity_ver()

        self._run_basic_prelude()
        if self.experiments:
            self._run_all_exps()
        if self.analyses:
            self._run_all_anals()
        self._has_run = True

    @ContextDecorator(ACTIVITIES.RUN)
    def _interactive_session(self, clargs=None):
        """
        docstring
        :return:
        """
        self.invocation = INVOCATION.HOOK
        self.invoker = get_external_caller()
        self._orient(clargs)

        if not self._oriented:
            raise XanityNotOrientedError

        self._resolve_requests()
        self._purge_dangling_experiments()
        # self._load_required_modules()
        # self._resolve_associations()
        self._process_parameters()

        self.n_total_exps = sum([len(item.success) for item in self.experiments.values()])
        self.n_total_anals = sum([len(item.experiments) for item in self.analyses.values()])

        if not self._check_environment():
            print('\n\n'
                  'looks like you\'re not inside the correct conda environment. \n'
                  'If you\'re using an IDE or calling a script directly, \n'
                  'please be sure you\'re using the python inside the \n'
                  'conda environment at path:\n{}\n\n'.format(self.conf_files.conda_env))
            raise SystemExit(1)
        # if not self.check_conda():
        #     print('\n\n'
        #           'looks like you\'ve made some changes '
        #           'to your conda environment file....\n'
        #           'please issue \'xanity setup\' to resolve the new one')
        #     raise SystemExit(1)

        self._check_xanity_ver()

        self._run_basic_prelude()
        # if self.experiments:
        #     self._run_all_exps()
        # if self.analyses:
        #     self._run_all_anals()
        # self._has_run = True

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_basic_prelude(self):
        # set global root dirs and do some basic path operations
        os.chdir(self.project_root)

        # create logger
        # self._init_logger()
        lsh = logging.StreamHandler(sys.stdout)
        if self.experiments:
            lsh.setFormatter(
                logging.Formatter(self.exp_data_dir.split('/')[-1] + ' %(asctime)s :%(levelname)s: %(message)s'))
        else:
            lsh.setFormatter(logging.Formatter(' %(asctime)s :%(levelname)s: %(message)s'))
        lsh.setLevel(logging.DEBUG)
        self.logger.addHandler(lsh)

        # print some info
        self.logger.info(
            '\n'
            '################################################################################\n'
            '## \n'
            '## \'run\' called at {} \n'
            '## {}\n'
            '## xanity_root: {} \n'
            '################################################################################\n'
            '\n'.format(
                datetime.datetime.fromtimestamp(time.mktime(self.start_time)).strftime('%Y-%m-%d %H:%M:%S'),
                vars(self.args),
                self.project_root)
        )

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_exp_prelude(self):
        """
            bunch of meta-level setup for subsequent experiments
        """
        # add root logger to write files
        self._attach_root_logger_fh()

        if not self.args.debug:
            # dump bookkeeping
            self._archive_source_tree()
            self._save_conda_snapshot()

        # print number of subexperiments found:
        for exp in self.experiments.keys():
            if len(self.experiments[exp].paramsets) > 1:
                self.logger.info(
                    '\n'
                    '################################################################################\n'
                    '##  experiment: {} has {} subexperiments:\n'.format(exp, len(self.experiments[exp].paramsets))
                    + '\n'.join(['##     exp #{}: {}'.format(i, param) for i, param in
                                 enumerate(self.experiments[exp].paramsets)]) + '\n'
                    + '################################################################################'
                )

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_anal_prelude(self):
        pass

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_all_exps(self):
        # do all experiments of interest

        # make data dir --- should be brand spanking new -- but just in case....
        os.makedirs(self.exp_data_dir, exist_ok=True) if PY_SYSVER == 3 else os.makedirs(self.exp_data_dir)

        self._run_exp_prelude()

        # sys.path.append(self.paths.experiments)
        for experiment in self.experiments.values():
            for index, _ in enumerate(experiment.success):
                self._run_one_exp(experiment, index)
        # sys.path.remove(self.paths.experiments)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_all_anals(self):
        # do all analyses
        self._parse_anal_data()

        self._run_anal_prelude()

        all_dirs = self.anal_data_dir

        for d in all_dirs:
            self.anal_data_dir = d
            # sys.path.append(self.paths.analyses)
            for anal_ind, analysis in enumerate(self.analyses.values()):
                analysis.success = []
                for exp_ind, exp in enumerate(analysis.experiments.values()):
                    self._run_one_anal(analysis, exp, anal_ind, exp_ind)
            # sys.path.remove(self.paths.analyses)

    @ContextDecorator(ACTIVITIES.EXP)
    def _run_one_exp(self, experiment, index):

        # make subexp data dir
        if os.path.isdir(experiment.subexp_dirs[index]):
            print('run data directory was already created... something\'s wrong')
            raise SystemExit(1)
        os.makedirs(experiment.subexp_dirs[index], exist_ok=False) if PY_SYSVER == 3 else os.makedirs(
            experiment.subexp_dirs[index])

        self.status.focus = experiment
        self.status.sub_ind = index
        self.status.params = experiment.paramsets[index]
        self.status.data_dir = experiment.subexp_dirs[index]

        # set some environment variablves for the benefit of any downstream shells
        os.environ['XANITY_DEBUG'] = str(self.args.debug)
        os.environ['XANITY_LOGGING'] = str(self.args.logging)
        os.environ['XANITY_DATA_DIR'] = str(experiment.subexp_dirs[index])

        if not self.args.debug:
            tfh = logging.FileHandler(filename=os.path.join(experiment.subexp_dirs[index], experiment.name + '.xanity.log'))
            tfh.setFormatter(logging.Formatter('%(asctime)s :%(levelname)s: %(message)s'))
            tfh.setLevel(logging.DEBUG)
            self.logger.addHandler(tfh)

        self.logger.info(
            "\n"
            "################################################################################\n"
            "## \n"
            "##   starting experiment #{} ({}/{}) \'{}\'\n"
            "##   {}\n"
            "## \n"
            "################################################################################\n"
            "\n".format(index, index + 1, len(experiment.success), experiment.name, self.status.params))

        try:
            opwd = os.getcwd()
            os.chdir(self.status.data_dir)
            sys.path.append(self.paths.experiments)

            if self.args.profile:
                profile.runctx(
                    'module.main(**paramdict)',
                    {},
                    {'module': experiment.module, 'paramdict': self.status.params},
                    os.path.join(experiment.subexp_dirs[index], experiment.name + '.profile'))
            else:
                experiment.module.main(**self.status.params)

            experiment.success[index] = True
            self.logger.info('experiment {} was successful'.format(experiment.name))

        except (KeyboardInterrupt, BdbQuit) as the_interrupt:
            self.savemetadata()
            raise the_interrupt

        except Exception:
            msg = traceback.print_exc()
            if msg is not None:
                self.logger.error(msg)

            experiment.success[index] = False
            self.logger.info('experiment {} was NOT successful'.format(experiment.name))

        finally:
            if 'tfh' in locals() and hasattr(self, 'logger'):
                self.logger.removeHandler(tfh)
            os.chdir(opwd)
            sys.path.remove(self.paths.experiments)
            gc.collect()

    @ContextDecorator(ACTIVITIES.ANAL)
    def _run_one_anal(self, analysis, experiment, analysis_ind=None, exp_ind=None):
        self.status.focus = analysis
        self.status.sub_ind = experiment
        self.status.data_dir = self.anal_data_dir

        # set some environment variablves for the benefit of any children's shells
        os.environ['XANITY_DEBUG'] = str(self.args.debug)
        os.environ['XANITY_LOGGING'] = str(self.args.logging)
        os.environ['XANITY_DATA_DIR'] = str(self.status.data_dir)

        #        if not self.args.debug:
        #            tfh = logging.FileHandler(
        #               filename=os.path.join(self.analyses[analysis].subexp_dirs[index],
        #               analysis + '.log'))
        #            tfh.setFormatter(logging.Formatter('%(asctime)s :%(levelname)s: %(message)s'))
        #            tfh.setLevel(logging.DEBUG)
        #            self.logger.addHandler(tfh)

        self.logger.info(
            "\n"
            "################################################################################\n"
            "##                                     \n"
            "##  starting analysis:  {} (#{} of {}) \n"
            "##      -  experiment:  {} (#{} of {}) \n"
            "##      - total anals:  {}             \n"
            "##      - data   path:  {}             \n"
            "################################################################################\n"
            "\n".format(
                analysis.name, analysis_ind + 1, len(self.analyses),
                experiment.name, exp_ind + 1, len(analysis.experiments),
                self.n_total_anals,
                self.status.data_dir
            )
        )

        try:
            opwd = os.getcwd()
            os.chdir(self.status.data_dir)
            sys.path.append(self.paths.analyses)

            if self.args.profile:
                profile.runctx(
                    'module.main(data_dir)',
                    {},
                    {'module': analysis.module, 'data_dir': self.status.data_dir},
                    os.path.join(self.status.data_dir, analysis.name + '.profile'))
            else:
                analysis.module.main(self.status.data_dir)

            analysis.success.append(True)
            self.logger.info('analysis {} was successful'.format(analysis.name))

        except KeyboardInterrupt as e:
            self.savemetadata()
            raise e

        except Exception:
            msg = traceback.print_exc()
            if msg is not None:
                self.logger.error(msg)

            analysis.success.append(False)
            self.logger.info('analysis {} was NOT successful'.format(analysis.name))

        finally:
            # if 'tfh' in locals():
            #     self.logger.removeHandler(tfh)
            os.chdir(opwd)
            sys.path.remove(self.paths.analyses)
            gc.collect()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _check_environment(self):
        return self.conf_files.conda_env in os.path.abspath(sys.executable)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _list_avail_experiments(self, names=None):
        if not self.project_root:
            raise XanityNoProjectRootError

        return list_modules_at_path(self.paths.experiments, names=names)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _list_avail_analyses(self, names=None):
        if not self.project_root:
            raise XanityNoProjectRootError

        return list_modules_at_path(self.paths.analyses, names=names)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _freeze_conda(self):
        open(self.conf_files.conda_hash, mode='w').write(self._hash_conda_env_file())
        open(self.conf_files.env_hash, mode='w').write(self._hash_conda_env())
        assert self._check_conda_file()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _check_xanity_ver(self):
        result = True
        try:
            sys_xanity = os.environ['XANITY_HOST_VER']
            if sys_xanity:
                import xanity as xanity_module
                myver = xanity_module.__version__
                result = myver == sys_xanity
                print('\n'
                      'system xanity version: {}\n'
                      'conda env xanity vers: {}\n'
                      '\n'.format(sys_xanity, myver)
                      )
        except Exception:
            pass

        return result

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _check_conda_env(self):
        if not os.path.isfile(self.conf_files.env_hash):
            return False
        conda_env_hash = self._hash_conda_env()
        saved_hash = open(self.conf_files.env_hash, mode='r').read()
        return conda_env_hash == saved_hash

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _check_conda_file(self):
        if not os.path.isfile(self.conf_files.conda_hash):
            return False
        conda_hash = self._hash_conda_env_file()
        saved_hash = open(self.conf_files.conda_hash, mode='r').read()
        return conda_hash == saved_hash

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _check_conda(self):
        return self._check_conda_env() and self._check_conda_file()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _hash_conda_env_file(self):
        return digest_file(self.conf_files.conda_env_file)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _hash_conda_env(self):
        #conda_env_name = open(os.path.join(self.paths.xanity_data, 'UUID'), 'r').read().split('\n')[0].strip()
        conda_env_path = os.path.join(self.paths.xanity_data, 'conda_env')
        try:
            # conda_env_contents = ''.join(sorted(str(subprocess.check_output([
            #     # 'bash', '-c', 'source xanity-enable-conda.sh 2>&1 /dev/null && conda list -n {}'.format(conda_env_name)
            #     'bash', '-lc', 'conda list -n {}'.format(conda_env_name)  # xanity(bash) makes sure conda is on path :)
            # ]).decode()).replace(' ', '').split()))
            conda_env_contents = ''.join(sorted(str(subprocess.check_output([
                'bash', '-ic', 'conda list -p {}'.format(conda_env_path)  # xanity(bash) makes sure conda is on path :)
            ]).decode()).replace(' ', '').split()))
        except subprocess.CalledProcessError:
            return None
        conda_env_contents = conda_env_contents.replace(' ', '')
        return digest_string(conda_env_contents)

    """
    the following private methods are deprecated:
    """

    # def _trip_hooks(self, item, hookname):
    #     """ this will trip all hooks.
    #     they each will check self.status.activity to see whether it's appropriate
    #     to fire"""
    #     raise XanityDeprecationError
    #     # assert hookname in dir(self), 'thats not a hook'
    #     # self.status.tripping = hookname
    #     # self.status.focus = item
    #     # # item.module = importlib.reload(item.module)
    #     # self._get_live_module(item.module_path)
    #     # self.status.focus = None
    #     # self.status.tripping = None
    #
    # def _catch_trip(self):
    #     raise XanityDeprecationError
    #     # if self.status.tripping == stack()[1][3]:
    #     #     return True
    #     # else:
    #     #     return False

    """
    the following are all public methods -- DO NOT USE INTERNALLY --
    """
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def subprocess(self, command):
        cmd = shsplit('bash -ic \'source {} && conda activate {} && {}\''.format(self._rcfile, self._env_path, command))
        return subprocess.Popen(cmd, shell=True)

    @property
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_prelude(self):
        return open(self.conf_files.shell_prelude, mode='r').read()

    @property
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_conclude(self):
        return open(self.conf_files.shell_conclude, mode='r').read()

    @shell_prelude.setter
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_prelude(self, value):
        if isinstance(value, str):
            value = [value]
        else:
            value = list(value)

        result = open(self.conf_files.shell_prelude, mode='w').write('\n'.join(value))

        if result is None:
            print('wrote new shell prelude script. please restart xanity.')
            raise SystemExit

        else:
            raise NotImplementedError

    @shell_prelude.setter
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_conclude(self, value):
        if isinstance(value, str):
            value = [value]
        else:
            value = list(value)

        result = open(self.conf_files.shell_prelude, mode='w').write('\n'.join(value))
        if result is None:
            print('wrote new shell conclude script. please restart xanity.')
            raise SystemExit

        else:
            raise NotImplementedError

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def run(self, clargs=None):
        self.invocation = INVOCATION.HOOK
        self.invoker = get_external_caller()
        self._orient(clargs)
        self._absolute_trigger()

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def find_recent_data(self):
        return self._find_recent_run_path()

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def savemetadata(self):
        if ACTIVITIES.EXP in self.status.act_tags:
            del self.logger
            for exp in self.avail_experiments.values():
                del exp.module
            for anal in self.avail_analyses.values():
                del anal.module
            pickle_dump(self, os.path.join(self.exp_data_dir, 'xanity_metadata.dill'))

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def load_checkpoint(self, checkpoint_name, variables=None, overwrite=False):
        if not self.args.loadcp:
            return None

        assert isinstance(checkpoint_name, str), 'can only save one checkpoint at a time!'

        if isinstance(variables, str):
            variables = [variables]
            solo = True
        else:
            solo = False

        cp_dir = os.path.join(self.paths.checkpoints, self.status.focus.name, checkpoint_name)
        # cp_files = [os.path.join(self.paths.checkpoints, self.status.focus.name, var + '.pkl') for var in checkpoints]

        if os.path.isdir(cp_dir):
        
            for root, dirs, files in os.walk(cp_dir):
                if os.path.join(cp_dir, 'xanity_variables') in root:
                    continue

                # s = os.path.join(cp_dir, item)
                # d = os.path.join(self.status.data_dir, item)

                # if os.path.isfile(s):
                #     os.link(s, d)
                # elif os.path.isdir(s):
                #     shutil.copytree(s, d, copy_function=os.link)

                for dir in dirs:
                    if dir != 'xanity_variables':
                        try:
                            os.mkdir(os.path.join(self.status.data_dir, root.split(cp_dir)[1], dir))
                        except OSError:
                            pass

                for f in files:
                    s = os.path.join(root, f)
                    d = os.path.join(self.status.data_dir, root.split(cp_dir)[1], f)
                    if os.path.isfile(d):
                        if overwrite:
                            os.remove(d)
                            os.link(s, d)
                        else:
                            pass
                    else:
                        os.link(s, d)

            vardir = os.path.join(cp_dir, 'xanity_variables')
            
            rvars = []
            if os.path.isdir(vardir) and variables is not None:
                    
                available = [v.split('.pkl')[0] for v in os.listdir(vardir)]
                
                for var in variables:
                    if var not in available:
                        rvars.append(None)
                        
                    else:
                        rvars.append(pickle_load(os.path.join(vardir, var+'.pkl')))

            if rvars:
                if solo:
                    return rvars[0]
                else:
                    return rvars
            else:
                return True

        else:
            return [False]*len(variables) if variables is not None and not solo else False

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def save_checkpoint(self, checkpoint_name, variables=None, cwd=True, overwrite=False):
        if not self.args.savecp:
            return False

        assert isinstance(checkpoint_name, str), 'can only save one checkpoint at a time!'
        
        cp_dir = os.path.join(self.paths.checkpoints,
                                     self.status.focus.name,
                                     checkpoint_name)
                                     
        if variables is not None:
            variables = [variables] if not isinstance(variables, (list, tuple)) else variables
            args = get_arg_names()
            varnames = None

            for item in args[1:]:
                if 'variables' in item.split('=')[0]:
                    varnames = [iitem.strip('\' []()') for iitem in item.split('=')[1].split(',')]

            if not varnames:
                varnames = [iitem.strip('\' [()]') for iitem in args[1].split(',')]

            assert len(variables) == len(varnames)

            cp_files = [os.path.join(cp_dir,
                                     'xanity_variables',
                                     var + '.pkl')
                        for var in varnames]

            for item, file in zip(variables, cp_files):
                if not os.path.isfile(file) or overwrite:
                    if not os.path.isdir(os.path.split(file)[0]):
                        os.makedirs(os.path.split(file)[0])
                    pickle_dump(item, file)

        if cwd:
            # saving runpath in file-system
            if not os.path.isdir(cp_dir):
                os.makedirs(cp_dir)
                        
            for root, dirs, files in os.walk(self.status.data_dir):
                # s = os.path.join(self.status.data_dir, item)
                # d = os.path.join(cp_dir, item)

                for dir in dirs:
                    try:
                        os.makedirs(os.path.join(cp_dir, root.split(self.status.data_dir)[1], dir))
                    except OSError:
                        pass

                for f in files:
                    if f.endswith('xanity.log'):
                        continue
                    s = os.path.join(root, f)
                    d = os.path.join(cp_dir, root.split(self.status.data_dir)[1], f)

                    if not os.path.isfile(d):
                        os.link(s, d)
                    elif overwrite:
                        os.remove(d)
                        os.link(s,d)
                        
                # elif os.path.isdir(s):
                #     try:
                #         shutil.copytree(s, d, copy_function=os.link)
                #     except OSError:
                #         shutil.copytree(s, d)

            return True

        else:

            return True

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def save_variable(self, value):
        # inspect.stack( #lines of context )[stack_idx][code context][codes lines]
        names = get_arg_names()
        datapath = os.path.join(self.status.data_dir, DIRNAMES.SAVED_VARS)
        os.makedirs(datapath, exist_ok=True) if PY_SYSVER == 3 else os.makedirs(datapath)
        for name in names:
            pickle_dump(value, os.path.join(datapath, name + '.dill'))

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def load_variable(self, name):

        datapaths = []
        if self.status.data_dir is None:
            self.status.data_dir = self.find_recent_data()

        for base, sdirs, files in os.walk(self.status.data_dir):
            sdirs.sort()
            if DIRNAMES.SAVED_VARS in sdirs:
                datapaths.append(os.path.join(base, DIRNAMES.SAVED_VARS))

        vals = []
        for dpath in datapaths:
            vals.append(pickle_load(os.path.join(dpath, name + '.dill')))

        return vals, datapaths

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def persistent(self, name, value=None):
        if ACTIVITIES.EXP in self.status.act_tags or ACTIVITIES.ANAL in self.status.act_tags:

            filename = os.path.join(self.paths.persistent_data, '{}.dill'.format(name))

            if value is not None and not os.path.isfile(filename):
                # set if it's not already there:
                pickle_dump(value, filename)
                return value

            # load the saved value and return it:
            if os.path.isfile(filename):
                return pickle_load(filename)
            else:
                return None

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def log(self, message):
        self.logger.info(message)

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def report_status(self):
        if hasattr(self, 'paths') and hasattr(self.paths, 'xanity_data'):
            # uuid = open(os.path.join(self.paths.xanity_data, 'UUID')).read() if os.path.isfile(
            #     os.path.join(self.paths.xanity_data, 'UUID')) else None
            setup_complete = True if self._check_conda else False
            reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode()
            installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
            req_packages = open(os.path.join(self.project_root, 'conda_environment.yaml'), 'r').read()
            req_packages = [line.lstrip(' -').split('#')[0].rstrip() if not line.lstrip().startswith('#') else '' for
                            line in req_packages.split('\n')]
            req_packages = list(filter(lambda item: bool(item), req_packages))
            req_start = [True if 'dependencies' in item else False for item in req_packages]
            req_start = req_start.index(1) + 1
            req_packages = req_packages[req_start:]
            missing_packages = [
                item if not any([item in item2 for item2 in installed_packages]) and not 'python' in item else None for
                item in req_packages]
            missing_packages = list(filter(lambda item: bool(item), missing_packages))
            print(
                '\n'
                '        conda env path: {}\n'
                '        setup complete: {}\n'
                '    installed packages: {}\n'
                '      missing packages: {}\n'
                ''.format(
                    self.paths.conda_env,
                    setup_complete,
                    len(installed_packages),
                    '\n                        {}\n'.join(missing_packages) if missing_packages else None
                )
            )

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def experiment_parameters(self, parameters_dict):
        # if self._catch_trip():
        #     self.status.focus.param_dict = parameters_dict
        caller_name = file2mod(get_external_caller())
        self._exp_paramset_requests[caller_name] = parameters_dict

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def associated_experiments(self, experiment_list):
        # if self._catch_trip():
        #     if not all([name in self.avail_experiments for name in experiment_list]):
        #         print('analysis list of associated experiments contains an unknown xanity experiment')
        #     self.status.focus.experiments.update(
        #         {exp: self.avail_experiments[exp] for exp in experiment_list if exp in self.avail_experiments})
        #     [self.avail_experiments[name].analyses.update({self.status.focus.name: self.status.focus}) for name in
        #      experiment_list if name in self.avail_experiments]
        if not isinstance(experiment_list, list):
            if isinstance(experiment_list, str):
                experiment_list = [experiment_list]
            else:
                print('provide associations as either single string or list of strings')
                raise SystemExit

        caller_name = file2mod(get_external_caller())
        if caller_name not in self._registered_associations:
            self._registered_associations[caller_name] = set(experiment_list)
        else:
            self._registered_associations[caller_name] = self._registered_associations[caller_name].update(
                experiment_list)

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def analyze_this(self):
        # if self._catch_trip():
        #     cand_anals = list(
        #         filter(lambda item: self.status.focus.name in item.experiments, self.avail_analyses.values()))
        #     for anal in cand_anals:
        #         if anal.name not in self.analyses:
        #             self.analyses.update({anal.name: anal})

        caller_name = file2mod(get_external_caller())
        self._exps_requesting_analysis.add(caller_name)

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def trials(self, number_of_trials):
        caller_name = file2mod(get_external_caller())
        self._trial_requests.update({caller_name: number_of_trials})

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def subdir(self, name):
        path = os.path.join(self.status.data_dir, name)
        try:
            os.makedirs(path)
        except OSError:
            pass
        return path





