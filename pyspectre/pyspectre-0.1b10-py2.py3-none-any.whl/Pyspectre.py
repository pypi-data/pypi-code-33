import signal
import time
import re
import tempfile
import os
import shutil
import numpy as np
import libpsf
import tarfile
import threading
from multiprocessing.managers import BaseManager
from multiprocessing import Lock

from io import BytesIO
from hashlib import sha1 as filehashfn
from textwrap import wrap as textwrap

from .spectre import get_REPLWrapper_in_another_process, get_REPLWrapper_in_this_process
from .spectre.skill_interface import Accelerated_scl_interface

from . import default_spectre_binary, default_rcfile, default_spectre_env
from . import pyspectre_path, pyspectre_ahdl_lib, pyspectre_ckt_dir, pyspectre_sim_dir

_spectre_env_flag = False
_rcfile = None
_spectre_env = None
_spectre_binary = default_spectre_binary

float_fmt_string = '{:+13.6e}'
local_sim_db_relpath = 'PYSPECTRE_AHDL_SIM'
local_ship_db_relpath = 'PYSPECTRE_AHDL_SHIP'


class LockManager(BaseManager):
    pass


try:
    LockManager.register('global_lock')
    global_manager = LockManager(address=('', 11223), authkey=b'iamjustalittlepyspectre')
    global_manager.connect()

except BaseException as e:
    global_lock = Lock()
    LockManager.register('global_lock', callable=lambda: global_lock)
    global_manager = LockManager(address=('', 11223), authkey=b'iamjustalittlepyspectre')
    global_manager.start()

# def get_rcfile():
#     return _rcfile
#
#
# def get_spectre_env():
#     return _spectre_env
#
#
# def get_spectre_binary():
#     return _spectre_binary


def set_rcfile(filepath=None):
    global _rcfile

    if filepath is None:
        filepath = default_rcfile

    filespec = os.path.expandvars(os.path.expanduser(filepath))

    if os.path.isfile(filespec):
        _rcfile = filespec


def set_spectre_env(env=None):
    global _spectre_env

    if env is None:
        _spectre_env = default_spectre_env
    else:
        assert isinstance(env, (tuple, list))
        assert all([isinstance(item, tuple) for item in env])
        assert all([isinstance(item, str) for pairs in env for item in pairs])
        _spectre_env = env


def set_spectre_binary(exepath=None):
    global _spectre_binary

    if exepath is None:
        _spectre_binary = default_spectre_binary
    else:
        specpath = os.path.expandvars(os.path.expanduser(exepath))
        assert os.path.isfile(specpath)
        _spectre_binary = specpath


def format_float(float):
    return float_fmt_string.format(float)


def format_vect(vect):
    return ' '.join([float_fmt_string.format(v) for v in vect.T.flatten()])


def _digest_file(filepath):
    return filehashfn(open(filepath, mode='rb').read().replace(' '.encode(), ''.encode())).hexdigest()


def _digest_string(string):
    return filehashfn(string.encode()).hexdigest()


def _get_patterns_for_internal_replacement(path_representation):
    return [r'^.\d*({})_.*[.]dep$'.format(path_representation)]


def hash_test(stimuli, time_vec):
    return str(filehashfn(
        str(tuple(np.concatenate([time_vec.ravel(), stimuli.ravel()]))).encode('utf-8')
    ).hexdigest()[:16])


def hash_tests(stimsets, time_vect):
    ids = []
    for tt in stimsets:
        ids.append(hash_test(tt, time_vect))
    return ids


class PyspectreUnresolvableError(ValueError):
    pass


class PwlInput(object):
    def __init__(self, name, max_n_points, parent=None):
        self.max_n_points = max_n_points
        self.name = name
        self.cname = '.'.join(name, parent) if parent else name
        self.default_value = None
        self.recent_value = None


class Parameter(object):
    def __init__(self, name, parent=None, ):
        if parent is not None:
            name = '.'.join(name, parent)
        self.name = name
        self.default_value = None
        self.recent_value = None


class Circuit(object):
    def __init__(self,
                 netlist=None,
                 simdirectory=None,
                 analysis_name='tran',
                 spectre_args=None,
                 pwl_inputs=None,
                 parameters=None,
                 ):

        # settle netlist file
        if not os.path.isfile(netlist):
            # print('netlist \"{}\" is not file'.format(netlist))
            # print('cwd: \"{}\"'.format(os.getcwd()))
            if not os.path.isdir(simdirectory):
                # print('simdirectory \"{}\" is not directory'.format(simdirectory))
                # print('cwd: \"{}\"'.format(os.getcwd()))
                raise IOError(
                    'unable to find spice netlist: netlist \"{}\" simdirectory: \"{}\"'.format(netlist, simdirectory))
            netlist = os.path.join(simdirectory, netlist)
            if not os.path.isfile(netlist):
                # print('netlist appended.  still not file: \"{}\"'.format(netlist))
                # print('cwd: \"{}\"'.format(os.getcwd()))
                raise IOError(
                    'unable to find spice netlist: netlist \"{}\" simdirectory: \"{}\"'.format(netlist, simdirectory))

        # settle simdir
        if simdirectory is not None and not os.path.isdir(simdirectory):
            simdirectory = os.path.dirname(netlist)

        if spectre_args is not None:
            if isinstance(spectre_args, list):
                spectre_args = ' '.join(spectre_args)
            elif isinstance(spectre_args, str):
                spectre_args = spectre_args

        if pwl_inputs is not None:
            if isinstance(pwl_inputs, PwlInput):
                pwl_inputs = tuple(pwl_inputs.cname, pwl_inputs)
            else:
                assert isinstance(pwl_inputs, (list, tuple))
                assert all([isinstance(item, PwlInput) for item in pwl_inputs])
                pwl_inputs = tuple(pwl_inputs)

        if parameters is not None:
            if isinstance(parameters, Parameter):
                parameters = tuple(parameters)
            else:
                assert isinstance(parameters, (list, tuple))
                assert all([isinstance(item, Parameter) for item in parameters])
                parameters = tuple(parameters)

        # build command
        # self.resolve_spectre_modes(spectre_output_mode, spectre_reader)

        self.spicefilepath = os.path.abspath(netlist)
        self.simdir = simdirectory
        self.analysis_name = analysis_name
        self.spectre_args = spectre_args
        self.pwl_inputs = pwl_inputs
        self.parameters = parameters
        self.tarball = None
        self.id = str(hash(self))

    # def resolve_spectre_modes(self, spectre_output_mode, spectre_reader):
    #     if spectre_output_mode is None and spectre_reader is None:
    #         self.spectre_output_mode = 'psfbin'
    #         self.spectre_reader = 'libpsf'
    #
    #     elif spectre_reader is not None and spectre_output_mode is None:
    #         assert spectre_reader in avail_readers
    #         self.spectre_reader = spectre_reader
    #         if spectre_reader == 'decida':
    #             self.spectre_output_mode = 'nutascii'
    #         elif spectre_reader == 'libpsf':
    #             self.spectre_output_mode = 'psfbin'
    #         else:
    #             raise NotImplementedError
    #
    #     elif spectre_output_mode is not None and spectre_reader is None:
    #         assert spectre_output_mode in avail_output_modes
    #         self.spectre_output_mode = spectre_output_mode
    #         if spectre_output_mode == 'ascii':
    #             self.spectre_reader = 'nutascii'
    #         elif spectre_output_mode == 'psfbin':
    #             self.spectre_reader = 'libpsf'
    #         else:
    #             raise NotImplementedError
    #
    #     else:
    #         assert spectre_reader in avail_readers
    #         self.spectre_reader = spectre_reader
    #         assert spectre_output_mode in avail_output_modes
    #         self.spectre_output_mode = spectre_output_mode

    def pack_up(self):
        self.tarball = self._make_tarball()

    def unpack(self, path):
        if not path:
            path = os.getcwd()
        self.tarball.seek(0)
        tb = tarfile.open(fileobj=self.tarball, mode='r:bz2')
        tb.extractall(path=path)
        tb.close()

    def _make_tarball(self):
        tarball = BytesIO()
        tb = tarfile.open(fileobj=tarball, mode='w:bz2')
        for item in os.listdir(self.simdir):
            tb.add(os.path.join(self.simdir, item), arcname=item)
        tb.close()
        return tarball

    def __hash__(self):
        return int(_digest_string(''.join(self._hash_files())), 16)

    def _hash_files(self):
        file_hashes = {}
        file_hashes.update({self.spicefilepath: _digest_file(self.spicefilepath)})

        if self.simdir is not None:
            for bdir, sdirs, files in os.walk(self.simdir):
                for ff in files:
                    filepath = os.path.join(bdir, ff)
                    file_hashes.update({filepath: _digest_file(filepath)})

        hashes = list(file_hashes.values())
        hashes.sort()
        return hashes

    def run_batch(self, stimuli, time_vec, signals='all'):
        if not signals or signals is None:
            signals = 'all'
        with Pyspectre(circuit=self, fork_repl=False) as pyspectre:
            results = pyspectre.run_batch(list_of_stimuli=stimuli, time_vec=time_vec, signames=signals)
        return results


class Pyspectre(object):

    def __init__(self,
                 circuit=None,
                 netlist=None,
                 simdirectory=None,
                 analysis_name='tran',
                 spectreargs=None,
                 logging=False,
                 pwl_inputs=None,
                 fork_repl=False,
                 ):

        if isinstance(threading.current_thread(), threading._MainThread):
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGABRT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

        if circuit is None:
            self.circuit = Circuit(
                netlist=netlist,
                simdirectory=simdirectory,
                analysis_name=analysis_name,
                spectre_args=spectreargs,
                pwl_inputs=pwl_inputs
            )
        else:
            self.circuit = circuit

        self.spectre_args = circuit.spectre_args
        self.spicefilepath = circuit.spicefilepath
        self.simdir = circuit.simdir
        self.analysis_name = circuit.analysis_name
        self.logging = logging
        self.pwl_inputs = circuit.pwl_inputs
        self.fork_repl = fork_repl

        self.original_simdir = None
        self.analysis_type = None
        self.dcsolution = None
        self.working_path = None
        self.results_dir = None
        self.quit = False
        self.spectre = None
        self.interface = None
        self.fresh = True
        self.pid = None
        self.commandct = None
        self.spectre = None
        self.cmd = None
        self.reader = 'libpsf'

        self._start_binary()

    def __del__(self):
        self._cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
        del self
        return

    def _signal_handler(self, signal, frame):
        self._cleanup()
        raise KeyboardInterrupt

    def _cleanup(self):
        self.quit = True
        try:
            self.interface.quit()
        except:
            try:
                self.spectre.child.terminate()
            except:
                try:
                    self.spectre.child.kill(9)
                except:
                    try:
                        os.kill(self.pid, 9)
                    except:
                        pass
        if not self.logging:
            try:
                shutil.rmtree(self.working_path)
            except:
                pass
        else:
            try:
                shutil.rmtree(self.results_dir)
            except:
                pass

    def _start_binary(self):
        global _spectre_env_flag

        if self.spectre is not None and self.spectre.child.isalive:
            return None
        if self.quit:
            return None

        # create/set shared working paths:
        os.makedirs(pyspectre_path, exist_ok=True)
        os.makedirs(pyspectre_ahdl_lib, exist_ok=True)
        os.makedirs(pyspectre_sim_dir, exist_ok=True)
        os.makedirs(pyspectre_ckt_dir, exist_ok=True)

        # place circuit dir in cache
        cache_target = os.path.join(pyspectre_ckt_dir, self.circuit.id)
        if self.circuit.id not in os.listdir(pyspectre_ckt_dir):
            # cache miss:
            if self.circuit.tarball is not None:
                # unpack circuit in correct cache directory
                self.original_simdir = self.simdir
                self.circuit.unpack(cache_target)

            else:
                if os.path.isdir(self.simdir):
                    # copy path to correct cache directory
                    shutil.copy(self.simdir, pyspectre_ckt_dir)
                    shutil.move(os.path.join(pyspectre_ckt_dir, os.path.split(self.simdir)[-1]),
                                cache_target)

                # copy spicefile
                os.makedirs(cache_target, exist_ok=True)
                shutil.copy(self.spicefilepath, cache_target)

        # setup working_path
        self.working_path = tempfile.mkdtemp(dir=pyspectre_sim_dir, prefix='')
        self.results_dir = os.path.join(self.working_path, 'psf')
        os.makedirs(self.results_dir, exist_ok=False)
        items = [os.path.join(cache_target, item) for item in os.listdir(cache_target)]
        for item in items:
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(self.working_path,os.path.split(item)[-1]))
            else:
                shutil.copy(item, self.working_path)

        self.original_simdir = self.simdir
        self.simdir = self.working_path
        self.spicefilepath = os.path.join(cache_target, os.path.split(self.spicefilepath)[-1])
        # self.spicefilepath = os.path.join(self.working_path, os.path.split(self.spicefilepath)[-1])

        # if you need to insure that there's enough memory for long waveforms:
        if self.pwl_inputs is not None:
            self._extend_pwl_defs_in_netlist()

        ahdl_sim_local = os.path.join(self.working_path, local_sim_db_relpath)
        ahdl_ship_local = os.path.join(self.working_path, local_ship_db_relpath)
        os.makedirs(ahdl_sim_local, exist_ok=True)
        os.makedirs(ahdl_ship_local, exist_ok=True)

        # add special environment vars, if needed
        if _spectre_env is not None and not _spectre_env_flag:
            """
            don't use dict here, becuause we're sensitive to order... must execute in order
            """
            for (var, value) in _spectre_env:
                val = os.path.expandvars(value)
                if '$' in val:
                    val = ':'.join([item for item in val.split(':') if '$' not in item])
                print('{}={}'.format(var, val))
                os.environ[var] = val
            _spectre_env_flag = True

        # build up actual command-line call
        if _rcfile is not None:
            invocation = 'bash --noprofile --norc -ic \'stty -icanon && source {} && '.format(_rcfile)
        else:
            invocation = 'bash --noprofile --norc -ic \'stty -icanon && '

        cmd_args = [
            '-64',
            '+interactive=skill',
            '-log -note -info -debug -warn -error ++aps=moderate',
            '-format=psfbin',
            '-mt',
        ]

        if self.spectre_args:
            if isinstance(self.spectre_args, str):
                cmd_args.append(self.spectre_args)
            elif isinstance(self.spectre_args, (list, tuple)):
                cmd_args.extend(list(self.spectre_args))

        if self.logging:
            cmd_args.append('+log=\"spectre.log\"')

        self.cmd = 'cd ' + self.working_path \
                   + ' && ' + _spectre_binary + ' ' + ' '.join(cmd_args) \
                   + ' -raw=\"{}\"'.format('raw') \
                   + ' -outdir=\"{}\"'.format(self.working_path)

        self.cmd = self.cmd + ' ' + self.spicefilepath

        full_cmd = invocation + self.cmd + '\''

        # self._load_relevant_lib_items()

        try:
            ootime = time.time()
            global_manager.global_lock().acquire(timeout=120)
            otime = time.time()
            print('spectre acquired lock in {:6.1f} ms'.format((otime-ootime)*1000))

            os.environ['CDS_AHDLCMI_SIMDB_DIR'] = ahdl_sim_local
            # os.environ['CDS_AHDLCMI_SHIPDB_DIR'] = ahdl_ship_local
            os.environ['CDS_AHDLCMI_SHIPDB_DIR'] = pyspectre_ahdl_lib
            os.environ['CDS_AHDLCMI_SHIPDB_COPY'] = 'YES'

            if self.fork_repl:
                self.spectre = get_REPLWrapper_in_another_process(
                    cmd_or_spawn=full_cmd,
                    orig_prompt=u'\n> ',
                    prompt_change=None)
            else:
                self.spectre = get_REPLWrapper_in_this_process(
                    cmd_or_spawn=full_cmd,
                    orig_prompt=u'\n> ',
                    prompt_change=None)

            self.fresh = False
            self.interface = Accelerated_scl_interface(self)
            self.pid = int(self.spectre.child.pid)
            self.commandct = 0
            self._resolve_analysis_type()

            scllogfile = os.path.join(cache_target,
                                      '.' + os.path.split(self.spicefilepath)[1].split('.scs')[0] + '.scllog')

            if os.path.isfile(scllogfile):
                os.link(scllogfile, os.path.join(self.working_path, 'scllog.scllog'))
                os.remove(scllogfile)
            else:
                raise RuntimeError('spectre did not create expected scllog file: {}'.format(scllogfile))

            print('started spectre in {:6.1f} ms'.format((time.time() - otime) * 1000))

        finally:
            global_manager.global_lock().release()
            # self._cache_local_ship_db()
            return None

    def _cache_local_ship_db(self):
        local_ship_db = os.path.join(self.working_path, local_ship_db_relpath)
        path_rep = self.working_path.replace('/', '_')
        id_rep = '_' + self.circuit.id

        local_lib_contents = os.listdir(local_ship_db)
        library_contents = os.listdir(pyspectre_ahdl_lib)
        equiv_lib_targs = [re.sub(path_rep, id_rep, item) for item in local_lib_contents]

        for local_item, lib_item in zip(local_lib_contents, equiv_lib_targs):
            if lib_item in library_contents:
                continue

            s = os.path.join(local_ship_db, local_item)
            d = os.path.join(pyspectre_ahdl_lib, lib_item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            elif os.path.isfile(s):
                shutil.copy(s, d)

                if any([re.match(pattern, local_item) for pattern in _get_patterns_for_internal_replacement(path_rep)]):
                    contents = open(d, mode='rb').read()
                    contents = contents.replace(path_rep.encode(), id_rep.encode())
                    open(d, mode='wb').write(contents)

    def _load_relevant_lib_items(self):
        local_ship_db = os.path.join(self.working_path, local_ship_db_relpath)
        path_rep = self.working_path.replace('/', '_')
        id_rep = '_' + self.circuit.id

        library_contents = os.listdir(pyspectre_ahdl_lib)
        relevent_lib_items = [item for item in library_contents if self.circuit.id in item]

        if relevent_lib_items:
            # found relevant library item... copy it into the local library
            for item in relevent_lib_items:
                newname = item.replace(id_rep, path_rep)
                s = os.path.join(pyspectre_ahdl_lib, item)
                d = os.path.join(local_ship_db, newname)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                elif os.path.isfile(s):
                    shutil.copy(s, d)

                    if any([re.match(pattern, item) for pattern in
                            _get_patterns_for_internal_replacement(id_rep)]):
                        contents = open(d, mode='rb').read()
                        contents = contents.replace(id_rep.encode(), path_rep.encode())
                        open(d, mode='wb').write(contents)

    def _read_file(self, filename, signames='all'):
        if not os.path.isfile(filename):
            filename = os.path.join(self.working_path, 'psf', filename)

        if isinstance(signames, str) and not signames == 'all':
            signames = [signames]

        if self.reader == 'libpsf':
            try:
                d = libpsf.PSFDataSet(filename)
            except IOError as e:
                print(
                    'ERROR: libpsf couldn\'t open file: '
                    '{}. See spectre simulation directory: {}'.format(filename, self.working_path)
                )
                raise e

            if isinstance(signames, str) and signames == 'all':
                return d.get_sweep_values().flatten(), np.array([d.get_signal(signame)
                                                                 for signame in d.get_signal_names()])
            else:
                return d.get_sweep_values().flatten(), np.array([d.get_signal(signame)
                                                                 for signame in signames])

        else:
            raise NotImplementedError

    def _resolve_analysis_type(self):
        self.analysis_type = self.interface.listanalysis()[self.analysis_name]
        # self.analysis = eval('Analyses.' + self.analysis_type.title() + '()')

    def _extend_pwl_defs_in_netlist(self):
        """
        create an alterate version of the netlist with reservation in the wave="*" assignment
        for a pwl signal as long as was requested
        :return:
        """

        modfile_suffix = '_PYSPECTRE_ALTERED'
        modfile_prefix = ''

        if self.pwl_inputs is None:
            return
        targets = [item.cname for item in self.pwl_inputs]
        target_names = [item.split('.')[-1] for item in targets]

        netlist = open(self.spicefilepath, mode='r').read().splitlines()

        # go through and find definitions:
        def_lines = {}
        context = []
        for line_no, line in enumerate(netlist):
            line = line.lstrip()
            if line.startswith('//'):
                continue
            toks = line.split()
            if len(toks) < 1:
                continue
            anchor = toks[0]
            if anchor == 'subckt':
                context.append(toks[1])
                continue
            if anchor == 'ends':
                context.pop()
                continue
            if anchor in target_names:
                this_guys_name = '.'.join(context) + '.' + anchor if context else anchor
                if this_guys_name in targets:
                    stopline = line_no
                    while re.match(r'.*\\\s*$', netlist[stopline]):
                        stopline += 1
                    def_lines.update({this_guys_name: {'PwlInput': target_names.index(anchor),
                                                       'range': range(line_no, stopline + 1)}})

        assert all([item in def_lines for item in targets])

        file_pattern = r'^.*(\s+file\s*=\s*\".+?\")'
        wave_pattern = r'^.*(\s+wave\s*=\s*\".+?\")'

        for name, patch_dict in def_lines.items():

            fulldef = ' '.join([netlist[ll].replace('\\', '').strip() for ll in patch_dict['range']])

            # remove all 'file' definitions

            if re.match(file_pattern, fulldef):
                fulldef = ' '.join(
                    [item.strip() for item in fulldef.split(re.match(file_pattern, fulldef).groups()[0])]).strip()

            # check and extend existing 'wave' definition
            if re.match(wave_pattern, fulldef):
                oldwave = re.match(wave_pattern, fulldef).groups()[0].split('=')[1].strip().strip('\"').split()
                fulldef = ' '.join(
                    [item.strip() for item in fulldef.split(re.match(wave_pattern, fulldef).groups()[0])]).strip()
                old_time = np.stack([float(t) for t in oldwave[::2]])
                old_vals = np.stack([float(v) for v in oldwave[1::2]])

                if old_time.size >= self.pwl_inputs[name].max_n_points:
                    continue
                else:
                    aug_len = self.pwl_inputs[name].max_n_points - old_time.size
                    ts = np.max(np.diff(old_time))
                    new_time = np.concatenate(
                        [old_time, np.linspace(old_time[-1] + ts, old_time[-1] + aug_len * ts, aug_len)])
                    new_vals = np.concatenate([old_vals, np.random.randn(aug_len)])

                    newval_str = ' '.join(
                        [' '.join([float_fmt_string] * 2).format(new_time[i], new_vals[i]) for i in range(aug_len)])

            else:
                # create brand-new 'wave' definition
                aug_len = self.pwl_inputs[patch_dict['PwlInput']].max_n_points
                ts = 1
                new_time = np.linspace(0, (aug_len - 1) * ts, aug_len)
                new_vals = np.random.randn(aug_len)

                newval_str = ' '.join(
                    [' '.join([float_fmt_string] * 2).format(new_time[i], new_vals[i]) for i in range(aug_len)])

            fulldef = ' '.join([fulldef, 'wave=[' + newval_str + ']'])
            fulldef = textwrap(fulldef, break_long_words=False, break_on_hyphens=False, subsequent_indent='    ')
            fulldef[:-1] = [item + ' \\' for item in fulldef[:-1]]  ## fwd slash on ends of lines
            # fulldef[1:] = ['+ ' + item for item in fulldef[1:]]     ## '+' at beginning of lines
            def_lines[name].update({'def': [ll + '\n' for ll in fulldef]})

        # all fixed up!
        # shutil.copy(self.spicefilepath, self.spicefilepath+'_bk')
        patchlist = [item['range'] for item in def_lines.values()]

        orig_parts = os.path.split(self.spicefilepath)
        orig_root = orig_parts[0]
        orig_base = orig_parts[1].split(os.path.extsep)
        orig_ext = os.path.extsep + orig_base[-1]
        orig_base = os.path.extsep.join(orig_base[:-1])

        target_file = os.path.join(orig_root, modfile_prefix+orig_base+modfile_suffix+orig_ext)
        with open(target_file, mode='w') as outfile:
            for line_no, line in enumerate(netlist):
                if any([line_no in r for r in patchlist]):
                    patch = [v for v in def_lines.values() if line_no in v['range']][0]
                    if line_no + 1 not in patch['range']:
                        outfile.writelines(patch['def'])
                        del patchlist[patchlist.index(patch['range'])]
                else:
                    outfile.write(line + '\n')

        self.spicefilepath = target_file

    def getparams(self, obj, paramnames):
        if isinstance(paramnames, str):
            paramnames = [paramnames]
        paramlist = self.interface.listparams(obj)
        if not all([name in paramlist for name in paramnames]):
            missing = [name not in paramlist for name in paramnames]
            print('coudln\'t find parameters named:{} in object:{}'.format(missing, obj))
            raise PyspectreUnresolvableError
        return {name: self.interface.getparametervalue(obj, name) for name in paramnames}

    def setparams(self, obj, paramdict):
        assert isinstance(paramdict, dict)
        for name, value in paramdict.items():
            self.interface.setparametervalue(obj, name, value)

    def setpwl(self, name, time_vec, volts):

        if isinstance(name, PwlInput):
            name = name.cname

        assert len(time_vec.shape) <= 2
        if len(time_vec.shape) == 2:
            assert np.min(time_vec.shape) == 1
            time_vec = time_vec.squeeze()

        assert len(volts.shape) <= 2
        if len(volts.shape) == 2:
            assert np.min(volts.shape) == 1
            volts = volts.squeeze()

        assert time_vec.size == volts.size, 'incompatible time vector'

        as_text = '[' + format_vect(np.stack([time_vec, volts])) + ']'

        self.setparams(name, {'wave': as_text})

    def close(self):
        self._cleanup()

    def runanalysis(self, analysis_name=None):
        if analysis_name is None:
            if self.analysis_name is not None:
                analysis_name = self.analysis_name
            else:
                raise ValueError('must specify an analysis name')

        self.interface.runanalysis(analysis_name)

    def setresultsdir(self, relpath=None):
        if relpath is None:
            if self.results_dir is not None:
                relpath = self.results_dir
            else:
                raise ValueError('no path specified')

        self.interface.setresultsdir(relpath)

    def readstatefile(self, filename=None):
        statedata = {}
        with open(os.path.join(self.working_path, filename)) as rdata:
            for line in rdata:
                if line.startswith('#'):
                    continue
                else:
                    tok = line.split()
                    statedata.update({tok[0]: float(tok[1])})

        return statedata

    def readdcfile(self):
        return self.readstatefile(self.analysis.dcfile)

    def readtranfile(self):
        return self.readstatefile(self.analysis.tranfile)

    def init(self, *args, **kwargs):
        """ use this for one-time calls which will persist forever"""
        self.analysis.init(self, *args, **kwargs)
        return self.analysis.dcfile

    def reset(self, *args, **kwargs):
        """ use this for one-time prep calls which will persist between analyses"""
        self.analysis.reset(self, *args, **kwargs)
        return self.analysis.tranfile

    def step(self, *args, **kwargs):
        """ use this for calls which have to be made before every step"""
        self.analysis.step(self, *args, **kwargs)
        return self.analysis.tranfile

    def get_data(self, signames=None):
        if isinstance(signames, (str)):
            signames = [signames]
        t, x = self.analysis.interpret_data(self, signames)
        return t, x

    def read_results(self, signal_names='all', analysis_name=None, analysis_type=None):
        if analysis_name is None:
            if self.analysis_name is not None:
                analysis_name = self.analysis_name
            else:
                raise ValueError('must specify analysis name')

        if analysis_type is None:
            if self.analysis_type is not None:
                analysis_type = self.analysis_type
            else:
                raise ValueError('must specify analysis type')

        return self._read_file(
            os.path.join(self.results_dir, '.'.join([analysis_name, analysis_type])),
            signames=signal_names
        )

    def run_batch(self, list_of_stimuli, time_vec, signames='all'):
        times = []
        signals = []

        print('starting batch of {} simulations.'.format(len(list_of_stimuli)))

        otime = time.time()
        for stimulus in list_of_stimuli:

            for i, input in enumerate(self.pwl_inputs):
                self.setpwl(input, time_vec=time_vec, volts=stimulus[i])

            self.setparams(self.analysis_name, {'stop': time_vec[-1]})
            self.runanalysis()

            restime, sigs = self.read_results(signal_names=signames)

            times.append(restime)
            signals.append(sigs)

        results = times, signals
        r_time = time.time()-otime

        if r_time < 1:
            print('batch took {:4.1f} ms'.format(r_time*1000))
        elif 60 > r_time >= 1:
            print('batch took {:4.1f} s'.format(r_time))
        elif r_time >= 60:
            print('batch took {:4.1f} m'.format(r_time/60))

        return results

