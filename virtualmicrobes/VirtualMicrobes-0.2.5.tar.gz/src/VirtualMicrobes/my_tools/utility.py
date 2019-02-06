'''
Created on Oct 22, 2014

@author: thocu
'''
import os.path
import glob
import numpy as np
import sys
import re

from functools import wraps
import multiprocessing as mp
import itertools
from collections import OrderedDict, namedtuple
from attrdict import AttrDict
import warnings
from shelve import Shelf, _ClosedDict
import collections
import random
import multiprocessing
from multiprocessing import TimeoutError
from multiprocessing.queues import SimpleQueue 
import signal
import psutil # @UnresolvedImport
import filecmp
import traceback
import errand_boy
import logging

try:
    import cPickle as pickle
    from cPickle import Pickler, Unpickler
except ImportError:
    import pickle
    from pickle import Pickler, Unpickler

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

ugly_globals = {'PhyloLinkerDict': {}, 'UniquePhyloKey':itertools.count(), 
                'graphs_as_subprocesses': False}


def flatten(nested_lists):
    return list(itertools.chain.from_iterable(nested_lists))

def queuedprocessor(as_subprocess=True):
    '''
    Decorator that can can cause a decorated method to be returned
    as a Task tuple, depending on the decorator argument.
    '''
    if not as_subprocess:
        print 'Not a subprocesses'
    def sub_process_wrapper(f):
        @wraps(f)
        def wrapper(obj, *args, **kwargs):
            run_subproc = True if kwargs.has_key('run_subproc') and kwargs['run_subproc'] else False
            if not as_subprocess or run_subproc :
                if run_subproc:
                    del kwargs['run_subproc']
                f(obj, *args, **kwargs)
                return 
            return obj, f.__name__, args, kwargs
        return wrapper
    return sub_process_wrapper

def subprocessor(as_subprocess=True):
    '''
    Decorator that can can cause a decorated function or method to be returned
    as a subprocess or simply evaluated, depending on the decorator argument.
    '''
    if not as_subprocess:
        print 'Not a subprocesses'
    def sub_process_wrapper(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not as_subprocess :
                f(*args, **kwargs)
                return 
            p = mp.Process(target=f, args=args, kwargs=kwargs)
            return p
        return wrapper
    return sub_process_wrapper

# https://gist.github.com/schlamar/2311116
def processify(func):
    '''Decorator to run a function as a process.
    
    Be sure that every argument and the return value is *pickable*. The created
    process is joined, so the code does not run in parallel.
    '''

    def process_func(q, *args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except Exception:
            ex_type, ex_value, tb = sys.exc_info()
            error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
            ret = None
        else:
            error = None

        q.put((ret, error))

    # register original function with different name
    # in sys.modules so it is pickable
    process_func.__name__ = func.__name__ + 'processify_func'
    setattr(sys.modules[__name__], process_func.__name__, process_func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        q = SimpleQueue() # potential fix for hanging multiprocess Queue http://stackoverflow.com/a/33733764
        p = multiprocessing.Process(target=process_func, args=[q] + list(args), kwargs=kwargs)
        p.start()
        ret, error = q.get()
        p.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = '%s (in subprocess)\n%s' % (ex_value.message, tb_str)
            raise ex_type(message)

        return ret
    return wrapper

from contextlib import contextmanager

@contextmanager
def errand_boy_server():
    socket_base='/tmp/errand-boy'
    from errand_boy.transports.unixsocket import UNIXSocketTransport
    from errand_boy.run import LOGGING
    logging.config.dictConfig(LOGGING)
    import time
    
    socket_path, socket_index = socket_base, 0
    while os.path.exists(socket_path):
        socket_path = '.'.join([socket_base, str(socket_index)])
        socket_index += 1
    
    transport = UNIXSocketTransport(socket_path=socket_path)
    server_as_subproc = subprocessor(as_subprocess=True)(transport.run_server)
    max_tries = 10
    for _ in range(max_tries):
        proc = server_as_subproc(pool_size=3, max_accepts=False)
        proc.start()
        time.sleep(10)
        if proc.is_alive():
            # the server is still alive after 10 sec
            # we are ready to 'yield'
            break
        # else, try again
    try:
        yield proc, socket_path
    finally:
        print 'killing errand-boy'
        proc.terminate()
        os.remove(socket_path)

def ensure_dir(d, message=None, remove_globs=[]):
    #d = os.path.dirname(f)
    pwd = os.getcwd()
    if os.path.exists(d):
        if remove_globs:
            print d, "exists. Removing files matching", " ".join([str(g) for g in remove_globs])
            for path, _dirs, _files in os.walk(d):
                os.chdir(path)
                for remove_glob in remove_globs:
                    map(os.remove, glob.glob(remove_glob))
            if message !=None:
                print message
        else:
            print d, "exists. Files may be overwritten."
            if message !=None:
                print message
        os.chdir(pwd) # change back to where we started               
    else:
        try:
            os.makedirs(d)
        except OSError:
            print 'could not make dir', d
            raise


# https://gist.github.com/audy/783125
# Shannon Diversity Index
# http://en.wikipedia.org/wiki/Shannon_index
def sdi(data):
    """ Given a hash { 'species': count } , returns the SDI
    
    >>> sdi({'a': 10, 'b': 20, 'c': 30,})
    1.0114042647073518"""
    
    from math import log as ln
    
    def p(n, N):
        """ Relative abundance """
        if n is  0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)
            
    N = sum(data.values())
    
    return -sum(p(n, N) for n in data.values() if n is not 0)

def padded_most_frequent(a, freq_cutoff):
    most_frequent = unique_count(a).T[0,:freq_cutoff]
    most_frequent = np.asarray(most_frequent, np.float)
    return pad_frequencies(most_frequent, freq_cutoff)
    

def unique_count(a):
    '''
    Count values and return value-count pairs sorted on counts (highest first)
    :param a:
    '''
    unique, count = np.unique(a, return_counts=True)
    counted_array = np.vstack(( unique, count)).T
    return counted_array[counted_array[:,1].argsort()][::-1]
        
def pad_frequencies(a, pad_to, pad_with=(np.nan, np.nan)):
    return np.pad(a, (0, max(pad_to-len(a),0)),                   
                  'constant', constant_values=pad_with)
    
def time_course_array(length):
    return np.full(length,np.nan,dtype=np.float64)

def grow_array(ar, factor=1.25):
    return np.resize(ar,(int(len(ar) * factor), ))

# http://stackoverflow.com/a/18348004   
def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T

 
ReactionScheme = namedtuple('ReactionScheme', ['reactants', 'products'])
     
Coord = namedtuple('Coord', ['x', 'y']) 

GridPos = namedtuple('GridPos', ['row', 'col']) 

PopulationWipe = namedtuple('PopulationWipe', ['interval', 'fraction'])

GeneTypeNumbers = namedtuple('GeneTypeNumbers', ['tf', 'enz', 'pump'])

ParamSpace = namedtuple('ParamSpace', ['base', 'lower', 'upper'])

MutationParamSpace = namedtuple('MutationParamSpace', ['base', 'lower', 'upper', 'min', 'max'])

GridSubDiv = namedtuple('GridSubDiv', ['row', 'col'])

SubEnv = namedtuple('SubEnv', ['influx_dict', 'sub_grid'])

MutationRates = namedtuple_with_defaults('MutationRates', [
                                             'chrom_dup', 
                                             'chrom_del', 
                                             'chrom_fiss', 
                                             'chrom_fuse', 
                                             'point_mutation',
                                             'tandem_dup', 
                                             'stretch_del', 
                                             'stretch_invert', 
                                             'stretch_translocate',
                                             'stretch_exp_lambda',
                                             'external_hgt' , 
                                             'internal_hgt',
                                             'regulatory_mutation',
                                             'reg_stretch_exp_lambda'],
                                         {'regulatory_mutation':0.0, # defaults for new fields, to allow loading older pickles without this definition
                                             'reg_stretch_exp_lambda':0.02}
                                         )
PointMutationRatios = namedtuple('PointMutationRatios', [
                                                         'v_max',
                                                         'ene_ks', 
                                                         'subs_ks',
                                                         'exporting',
                                                         'promoter',
                                                         'operator',
                                                         'eff_bound',
                                                         'eff_apo',
                                                         'ligand_ks',
                                                         'k_bind_op',
                                                         'ligand_class',
                                                         'bind',
                                                         'sense_external'
                                                         ])
RegulatorytMutationRatios = namedtuple('RegulatorytMutationRatios', [
                                                                     'translocate',
                                                                     'random_insert'
                                                                     ])

ETEtreeStruct = namedtuple('ETEtreeStruct', ['tree', 
                                             'named_node_dict',
                                             'node_name_to_phylo_node'
                                             ])

#http://stackoverflow.com/a/1275088
def Struct(*args, **kwargs):
    def init(self, *iargs, **ikwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
        for i in range(len(iargs)):
            setattr(self, args[i], iargs[i])
        for k,v in ikwargs.items():
            setattr(self, k, v)

    name = kwargs.pop("name", "MyStruct")
    kwargs.update(dict((k, None) for k in args))
    return type(name, (object,), {'__init__': init, '__slots__': kwargs.keys()})

SmallMol = Struct('influx', 
                  'concentration',
                  'diffusion', 
                  'degradation', 
                  'time_course',
                  'cum_time_course',  
                  name='SmallMol')
GeneProduct = Struct('concentration',
                     'diffusion', 
                     'degradation', 
                     'time_course',
                     'cum_time_course', 
                     'multiplicity', name='GeneProduct')

class ReusableIndexDict(object):
    
    class_version = '0.0'
    
    def __init__(self, keys=[], fixed_length=None, randomized=True):
        
        self.version = self.__class__.class_version
        
        self.randomized = randomized
        self.init_rand_gen()
        if fixed_length is not None and fixed_length < len(keys):
            raise Exception('setting fixed_length: {0} < len(keys):{1}'.format(fixed_length, len(keys)))
        
        self.filled_indices = [ True for _ in range(len(keys)) ]
        self.index_dict = OrderedDict()
        if fixed_length is not None:
            self._fixed = True
            for _ in range(max(0,fixed_length - len(self.filled_indices))):
                self.filled_indices.append(False)
        else:
            self._fixed = False
        if self.randomized:
            self.rand_gen.shuffle(keys)
        for i, k in enumerate(keys):
            self.index_dict[k] = i
    
    def init_rand_gen(self):
        self.rand_gen = random.Random(256)
    
    def index_key(self, key):
        try:
            i = self.index_dict[key]
        except KeyError:
            try:
                unfilled_indices = ( i for i,v in enumerate(self.filled_indices) if not v )
                if self.randomized:
                    i = self.rand_gen.choice(list(unfilled_indices))
                else:
                    i = next(unfilled_indices)
                self.index_dict[key] = i
                self.filled_indices[i] = True
            except (StopIteration, IndexError):
                if self._fixed:
                    raise
                i = len(self.filled_indices)
                self.filled_indices.append(True)
                self.index_dict[key] = i
        return i
            
    def remove_key(self, key):
        i = self.index_dict[key]
        self.filled_indices[i] = False
        del self.index_dict[key]  
        
    def keys(self):  
        return self.index_dict.keys()
    
    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added. 
        Adapted from recipe at http://code.activestate.com/recipes/521901-upgradable-pickles/
        '''
        version = float(self.version)
        if version < 1.:
            pass
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version

    def __getstate__(self):
        odict = self.__dict__.copy()
        return odict
        
    def __setstate__(self, d):
        self.__dict__ = d
        # upgrade class if it has an older version
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()
    
def get_unique_key(val):
    return val._unique_key

def get_from_linker(key):
    return ugly_globals['PhyloLinkerDict'][key]

map_forward_func = get_unique_key
map_backward_func = get_from_linker


class LinkThroughSequence(list):
    """A list that applies an arbitrary element
    function before returning and storing
    """
    
    __slots__ = []
    
    def __init__(self, data=[]):
        """Initialize the class"""
        super(LinkThroughSequence, self).__init__()
        for d in data:
            self.append(d)

    def __getitem__(self, ii):
        """Get a list item"""
        return map_backward_func(self[ii])

    def __delitem__(self, ii):
        """Delete an item"""
        del self[ii]

    def __setitem__(self, ii, val):
        self[ii] = map_forward_func(val)
        
    def __contains__(self, val):
        val = map_forward_func(val)
        return super(LinkThroughSequence, self).__contains__(val)
        
    def _pickle_repr(self):
        return self[:]
    
    @classmethod
    def _unpickle_repr(cls, pickle_repr):
        new_lts = LinkThroughSequence()
        for i in pickle_repr:
            super(LinkThroughSequence, new_lts).append(i)
        return new_lts
        
    def pop(self, index=-1):
        return map_backward_func(super(LinkThroughSequence, self).pop(index))
        
    def append(self, val):
        val = map_forward_func(val)
        super(LinkThroughSequence, self).append(val)

    def insert(self, ii, val):
        self.insert(ii, map_forward_func(val))
        
    def remove(self, val):
        val = map_forward_func(val)
        super(LinkThroughSequence, self).remove(val)
        
    def __iter__(self):
        for v in super(LinkThroughSequence,self).__iter__():
            yield map_backward_func(v) 

def linkthrough(f):
    def cf(self, new):
        cls = self.__class__
        if not isinstance(new, cls):
            new = cls(new)
        return f(self,new)
    return cf

class LinkThroughSet(set):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""
    
    __slots__ = []
    
    def __init__(self, data=[]):
        super(LinkThroughSet,self).__init__()
        for d in data:
            self.add(d)

    def add(self, el):
        super(LinkThroughSet,self).add(map_forward_func(el))
        
    def pop(self):
        return map_backward_func(super(LinkThroughSet,self).pop())
    
    def copy(self):
        return set.copy(self)

    @linkthrough
    def __and__(self, x):
        return set.__and__(self, x)

    @linkthrough
    def __or__(self, x):
        return set.__or__(self, x)
    
    @linkthrough
    def __sub__(self, x):
        return set.__sub__(self, x)

    @linkthrough
    def __iand__(self, x):
        return set.__iand__(self, x)

    @linkthrough
    def __isub__(self, x):
        return set.__isub__(self, x)

    @linkthrough
    def __ixor__(self, x):
        return set.__ixor__(self, x)

    @linkthrough
    def __ior__(self, x):
        return set.__ior__(self, x)        

    @linkthrough    
    def update(self, x):
        super(LinkThroughSet,self).update(x)

    @linkthrough        
    def difference(self, x):
        return set.difference(self, x)

    @linkthrough    
    def intersection(self, x):
        return set.intersection(self, x)
    
    @linkthrough        
    def difference_update(self, x):
        return set.difference_update(self, x)

    @linkthrough
    def symmetric_difference(self, x):
        return set.symmetric_difference(self, x)

    @linkthrough
    def union(self, x):
        return set.union(self, x)
    
    def __iter__(self):
        for v in super(LinkThroughSet,self).__iter__():
            yield map_backward_func(v)    
    
                    
    def _pickle_repr(self):
        '''
        Method used to create a pickle representation that does not lookup the
        'linked-through' values in this container. This makes it possible to 
        pickle an object which uses this container without going into deep 
        recursion. Moreover, this makes it usefull to keep such objects in a 
        Shelf like container themselves and 'partially' sync them to a the 
        shelf database, without incuring the cost of doing lookups of linked-through
        objects that reside in the shelf (requiring unpickling those).
        '''
        return set( [ v for v in super(LinkThroughSet,self).__iter__()])
    
    @classmethod
    def _unpickle_repr(cls, pickle_repr):
        '''
        This is the reverse of forming a _pickle_repr. It recasts the pickle_repr
        into a fully functional link-through container that has the map_forward and 
        map_backward functionality. 
        :param cls:
        :param pickle_repr:
        '''
        new_lts = LinkThroughSet()
        for i in pickle_repr:
            super(LinkThroughSet, new_lts).add(i)
        return new_lts
    
class PartialLinkThroughDict(collections.MutableMapping):
    '''
    Values objects can have a '_unique_key' attribute, in which case storage of the value is 
    linked through to the linker_dict. Otherwise, the value goes into the local storage of the
    PartialLinkThroughDict instance.
    '''
    
    def __init__(self, linker_dict, *args, **kwargs):
        self.store = OrderedDict()
        self.larder = linker_dict
        self.update(dict(*args, **kwargs))  # use the free update to set keys
        
    def set_larder(self, larder):
        self.larder = larder
        
    def close_larder(self):
        try:
            self.larder.close()
        except:
            pass
        
    def partial_sync(self, part):
        if isinstance(self.larder, FIFOLarder):
            self.larder.partial_sync(part)
        elif isinstance(self.larder, Shelf):
            print 'full sync in Shelf ojbect'
            self.larder.sync()

    def __getitem__(self, key):
        val = self.store[key]
        try:
            return self.larder[val]
        except (KeyError, TypeError):
            return val

    def __setitem__(self, key, value):
        if hasattr(value, '_unique_key') and value._unique_key is not None:
            self.store[key] = value._unique_key
            self.larder[value._unique_key] = value
        else:
            self.store[key] = value

    def __delitem__(self, key):
        val = self.store[key]
        try:
            del self.larder[val]
        except (KeyError, TypeError):
            pass
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

#TODO: give option to use a standard dictionary instead of a Shelf like database. 
# At the moment, the FIFOLarder does not serve a function, as there is no partial 
# shelving taking place.             
class FIFOLarder(Shelf): 
    '''
    Maintain a hybrid cached/pickled dictionary that presents as a normal dictionary.
    Postpone pickling of dictionary values until (partial)sync calls. This requires both
    the pickled and the cached dict to be checked when lookup en set operations are applied.
    The cache is an OrderedDict so that it can be 'partially' synced to pickle in FIFO order.
    This structure is usefull when new data coming in is still handled often and may regularly change, 
    while old data can be considered more stable and less likely to change, and thus amenable for more
    permanent storage.
    '''
    
    def __init__(self, filename, flag='c', protocol=None):
        import anydbm
        self.db_filename = filename
        self.dict = anydbm.open(filename, flag)
        if protocol is None:
            protocol = pickle.HIGHEST_PROTOCOL
        self._protocol = protocol
        #self.writeback = True # implementation assumes writeback = True
        self.cache = OrderedDict()
        
    def reopen_db(self, save_file = None, flag='c'):
        import anydbm
        if save_file is None:
            save_file = self.db_filename
        #print 'reopening FIFOLarder file', save_file
        self.db_filename = save_file
        self.dict = anydbm.open(save_file, flag)
            
    def keys(self):
        return set(self.dict.keys()) | set(self.cache.keys())

    def __len__(self):
        return len(self.keys())

    def has_key(self, key):
        return key in self

    def __contains__(self, key):
        return key in self.cache or key in self.dict 

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def __getitem__(self, key):
        try:
            value = self.cache[key]
        except KeyError:
            f = StringIO(self.dict[key])
            value = Unpickler(f).load()
            self.cache[key] = value
        return value

    def __setitem__(self, key, value):
        self.cache[key] = value

    def _setitem_pickled(self,key, value):
        #print key, 'to pickle dict'
        f = StringIO()
        p = Pickler(f, self._protocol)
        p.dump(value)
        self.dict[key] = f.getvalue()

    def __delitem__(self, key):
        found = False
        try:
            del self.dict[key]
            found = True
        except KeyError:
            pass
        try:
            del self.cache[key]
            found |= True
        except KeyError:
            pass
        if not found:
            raise KeyError

    def __del__(self):
        if not hasattr(self, '_protocol'):
            #__init__ didn't succeed, so don't bother closing
            return
        self.close()

    def sync(self):
        self.partial_sync(part=1.)
        
    def close(self):
        if hasattr(self.dict, 'sync'):
            self.dict.sync()
        try:
            self.dict.close()
        except AttributeError:
            pass
        # Catch errors that may happen when close is called from __del__
        # because CPython is in interpreter shutdown.
        try:
            self.dict = _ClosedDict()
        except (NameError, TypeError):
            self.dict = None
        
    def partial_sync(self, part, select=lambda x: True):
        '''
        sync a part of the dict to the pickled representation.
        
        @param part: can be an int or a float, specifying how much of cache will be 
        synced in FIFO order.
        '''
        cache_len = len(self.cache)
        selected = 0
        if isinstance(part, float):
            nr_items = int(len(self.cache)*part)
        else:
            nr_items = min(part, len(self.cache))
        for i, key in enumerate(self.cache): #reversed(self.cache) ):
            if i >= nr_items:
                break
            if select(self.cache[key]):
                entry = self.cache.pop(key)
                self._setitem_pickled(key, entry)
                selected += 1
        if hasattr(self.dict, 'sync'):
            print 'pickled', selected, 'items, decreasing cash by', str(cache_len - len(self.cache))
            self.dict.sync()
            self.dict.close()
            self.reopen_db()

def open_fifolarder(filename, flag='c', protocol=None):
    return FIFOLarder(filename, flag, protocol) 

# http://stackoverflow.com/a/16551730
class multifile(object):
    def __init__(self, files):
        self._files = files
    
    def __getattr__(self, attr, *args):
        return self._wrap(attr, *args)

    def _wrap(self, attr, *args):
        def g(*a, **kw):
            for f in self._files:
                res = getattr(f, attr, *args)(*a, **kw)
            return res
        return g
    
    def __enter__(self):
        #print 'returning self on enter'
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        for f in self._files:
            f.flush()
            if f not in [sys.__stdout__, sys.__stderr__]:
                f.close()
            elif f == sys.__stdout__:
                sys.stdout = sys.__stdout__
            else:
                sys.stderr = sys.__stderr__
                
# http://stackoverflow.com/a/16085543
# http://stackoverflow.com/a/9948173
class FormatMessageFile(file): 
    def __init__ (self, name, mode='r', replace_dict={'\r':'\n','\b':'',
                                                      r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?':''}, **kwargs):
        super(FormatMessageFile, self).__init__(name=name, mode=mode, **kwargs)
        self.replace_patterns_dict = dict() # NOTE: unordered ok
        for k,v in replace_dict.items():
            self.replace_patterns_dict[k] = re.compile(k), v
        print 'using regex replace to format messages for file', self.name
        
    def _subs_patterns(self, message):
        for _k, (p,r) in self.replace_patterns_dict.items():
            message = p.sub(r, message)
        return message
        
    def write(self, message):
        message = self._subs_patterns(message)
        super(FormatMessageFile,self).write(message)

#http://stackoverflow.com/a/25109391
def as_attrdict(val):
    if not isinstance(val, AttrDict):
        warnings.warn('cannot encode type {0}, so skipping it'.format(type(val)))
        return
        #raise TypeError('not AttrDict but {0}'.format(type(val)))
    return dict(val)

class pickles_adict(AttrDict):
    
    def __init__(self, *args, **kwargs):
        super(pickles_adict, self).__init__(*args, **kwargs)
    
    def __setstate__(self, state_dict):
        self.__setattr__('__dict__', state_dict, force=True)

def roulette_wheel_draw(events_rel_chances, rand_nr, non=0.):
    total_competition_value = sum([p for (_,p) in events_rel_chances])
    if total_competition_value <= 0.:
        print 'No competition value in any competitor'
    rand = rand_nr * ( total_competition_value + non )
    cumulative_competition = 0.
    event, competition_value ,index = None, 0, -1
    for i,(e,p) in enumerate(events_rel_chances):
        cumulative_competition += p
        if rand <= cumulative_competition:
            event, competition_value, index = e, p, i       
            break
    return event, competition_value, index

class CircularList(list):
    """ A list that wraps around instead of throwing an index error.
    
    Works like a regular list:
    >>> cl = CircularList([1,2,3])
    >>> cl
    [1, 2, 3]
    >>> cl[0]
    1
    >>> cl[-1]
    3
    >>> cl[2]
    3
    Except wraps around:
    >>> cl[3]
    1
    >>> cl[-4]
    3
    Slices work
    >>> cl[0:2]
    """
    
    def _get_slices(self, slc):
        #print slc.start, slc.stop
        slices = [] 
        if not self.__len__():
            return [slc]
        
        i_quot, i = divmod(slc.start,self.__len__() ) 
        j_quot, j = divmod(slc.stop,self.__len__() ) if slc.stop != sys.maxsize else (0, None)
        #print i_quot, i
        #print j_quot, j
        
        if i_quot == j_quot:
            if j is not None and j < i:
                slices.append(slice(i,None,None))
                slices.append(slice(None,j,None))
            else:
                slices.append(slice(i, j, None))
        elif j_quot > i_quot:
            if j > i:
                j = i
            slices.append(slice(i,None,None)) 
            slices.append(slice(None,j,None))
        return slices
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            slices = self._get_slices(key)
            return CircularList( sum( [ super(CircularList, self).__getitem__(slc) for slc in slices ], [] ))
        try:
            index = int(key)
            index = index % self.__len__()
            return super(CircularList, self).__getitem__(index)
        except ValueError:
            raise TypeError
    
    def __getslice__(self, i,j):
        return self.__getitem__(slice(i,j))
    
    def __setitem__(self, key, val):
        if isinstance(key, slice):
            slices = self._get_slices(key)
            if len(slices) == 1:
                super(CircularList, self).__setitem__(slices[0],val)
            else:
                val = val[:]
                for slc in slices:
                    part_list = super(CircularList, self).__getitem__(slc)
                    super(CircularList,self).__setitem__(slc, val[:len(part_list)])
                    del val[:len(part_list)]
                assert not len(val)
        else:
            try:
                index = int(key)
                index = index % self.__len__()
                super(CircularList, self).__setitem__(index, val)
            except ValueError:
                raise TypeError
    
    def __setslice__(self,i,j,seq):
        return self.__setitem__(slice(i,j),seq)
    
    def __delitem__(self, key):
        if isinstance(key, slice):
            for slc in self._get_slices(key):
                list.__delitem__(self, slc)
        else:
            try:
                index = int(key)
                index = index % self.__len__()
                return super(CircularList, self).__getitem__(index)
            except ValueError:
                raise TypeError
            
    def __delslice__(self, i,j):
        return self.__delitem__(slice(i,j))
    
    def __add__(self, other):
        return CircularList(super(CircularList,self).__add__(other))
    
    def __copy__(self):
        return self[:]
    
    def __deepcopy__(self, memo):
        return CircularList(super(CircularList,self).__deepcopy__(memo))
         
class OrderedDefaultdict(OrderedDict):
    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__ (self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self): # optional, for pickle support
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        #args = tuple() #test
        return type(self), args, None, None, self.iteritems()
    

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

class Consumer(multiprocessing.Process):
    '''
    Consumer Process that gets jobs from a Queue until receiving a
    'poison pill' job that will terminate the process.
    
    Jobs will timeout after a given time. 
    '''
    
    def __init__(self, task_queue, result_queue, task_timeout=120):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.timeout = task_timeout

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            #next_task = self.task_queue.pop(0)
            if next_task is None:
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                #self.task_queue.task_done()
                break
            #print '%s: %s' % (proc_name, next_task)
            answer = None
            try:
                with timeout(seconds=self.timeout):
                    answer = next_task()
            except TimeoutError:
                print 'process', proc_name, 'timed out'
            if self.result_queue is not None:
                self.result_queue.put(answer)
        return

class Task(object):
    '''
    Task object class used to present jobs to Consumer processes. Tasks are
    assumed to be method functions associated with a class instance.
    
    Task will except all errors generated by the method call so that the
    Consumer processing the Task will stay alive.
    '''
    
    
    def __init__(self, obj, func_name, args=[], kwargs=dict()): # NOTE: unordered ok
        self.obj = obj
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self):
        print 'start Task', self.func_name
        func = getattr(self.obj, self.func_name)
        return func(run_subproc=True, *self.args, **self.kwargs)
    
    def __str__(self):
        return 'function:{} args:{} kwargs:{}'.format(self.func_name, self.args, self.kwargs)

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def detect_rel_path_change(old_save_dir, load_file, 
                           mount_path_depth=4, 
                           abs_root='/linuxhome/tmp/'):
    """
    Detects the usage of a mounted path versus the abolute path on the server.
    
    old_save_dir : path
        Original simulation save path
    load_file : file_path
        Full path of the load file
    mount_path_depth : path
        
    :param abs_root:
    """
    
    load_file_path, lf_name = os.path.dirname(load_file), os.path.basename(load_file)
    if len(load_file_path.strip(os.sep).split(os.sep)) < mount_path_depth:
        # load_file can not be at mount_path
        return False
    abs_load_path = os.path.join(abs_root, *(load_file_path.split(os.sep)[mount_path_depth:]))
    abs_load_file = os.path.join(abs_load_path, lf_name)
    try:
        if os.path.samefile(load_file, abs_load_file): 
            # We are still running on the same machine
            if old_save_dir == abs_load_path:
                # we are still in the same simulation dir
                return True
                #return abs_root, os.path.join(os.sep, 
                #                              *(load_file_path.split(os.sep)[:mount_path_depth]))
    except OSError:
        return False
        # The file is not on the 'assumed' absolute path


def same_content(dir1, dir2):
    """
    Compare two directory trees content.
    Return False if they differ, True if they are the same.
    """
    print 'Comparing content of path\n{} to \n{} '.format(dir1, dir2)
    compared = filecmp.dircmp(dir1, dir2)
    if (compared.left_only or compared.right_only or compared.diff_files 
        or compared.funny_files):
        return False
    for subdir in compared.common_dirs:
        if not same_content(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            return False
    return True

def detect_sim_folder_move(stored_save_dir, load_path):  
    """
    Detect whether the load_path was placed in a different location from the
    original simulation path.
    
    Parameters
    ----------
    stored_save_dir : path
        original simulation directory
    load_path : path
        load file
    """
    stored_save_dir = os.path.abspath(stored_save_dir)
    current_save_dir = os.path.abspath(load_path)
    path_name_change = stored_save_dir != current_save_dir
    try:
        differing_content = not same_content(stored_save_dir, current_save_dir)
    except OSError:
        # We do not know the location of the stored_save_dir
        differing_content = None
    return path_name_change, differing_content

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        try:
            child.kill()
            print '+', 
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(children, timeout=1.)
    if including_parent:
        parent.kill()
    return parent
                
class ValueNotInRange(ValueError):
    pass

def within_range(val, rng):
    lower, upper = rng
    if not val >= lower and val <= upper:
        raise ValueNotInRange

def json_dumper(obj, *args, **kwargs): # http://stackoverflow.com/a/28174796
    #try:
    return obj.toJSON(*args, **kwargs)
    #except AttributeError:
    #    return obj.__dict__
#print json.dumps(some_big_object, default=dumper, indent=2)

def chunks(l, n):
    '''Yield successive n-sized chunks from l.'''
    for i in range(0, len(l), n):
        yield l[i:i+n]
