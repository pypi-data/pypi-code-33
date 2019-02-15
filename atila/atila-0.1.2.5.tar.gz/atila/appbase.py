from functools import wraps
from urllib.parse import unquote_plus, quote_plus, urljoin
import os
import inspect
from importlib import reload
from skitai import was as the_was
import time, threading
from .storage import Storage
from event_bus.exceptions import EventDoesntExist
import atila
from types import FunctionType
from . import decorators, wwwauth
    
class AppBase (decorators.Decorators, wwwauth.WWWAuth):    
    use_reloader = False
    debug = False
    auto_mount = True
    contrib_devel = False # make reloadable
    # Session
    securekey = None
    session_timeout = None

    #WWW-Authenticate    
    access_control_allow_origin = None
    access_control_max_age = 0    
    authenticate = None        
    realm = "App"
    users = {}    
    opaque = None
    
    def __init__ (self):
        decorators.Decorators.__init__ (self)
        self.module = None
        self.packagename = None
        self.wasc = None                
        self.logger = None
        self.store = Storage ()
        self.lock = threading.RLock ()
        
        self.mount_p = "/"
        self.path_suffix_len = 0
        self.mount_params = {}
        self.reloadables = {}
        self.last_reloaded = time.time ()        
        self.init_time = time.time ()
        
        self._maintern_funcs = {}  
        self._package_dirs = []           
        self._mount_option = {}
        self._started = False
        self._reloading = False        
        
        self._salt = None
        self._permission_map = {}
        
        self.store ["__last_maintern"] = 0.0
        self.store ["__maintern_count"] = 0
    
    def maintern (self):
        if not self._maintern_funcs:
            return
        now = time.time ()
        if (now - self.store ["__last_maintern"]) < self.config.get ("maintain_interval", 60):
            return
        
        was = the_was._get ()    
        with self.lock:
            for func in self._maintern_funcs.values ():
                func (was, now, self.store ["__maintern_count"])
        self.store ["__last_maintern"] = now
        self.store ["__maintern_count"] += 1
            
    def get_resource (self, *args):
        return self.joinpath ("resources", *args)
    
    def joinpath (self, *args):    
        return os.path.normpath (os.path.join (self.home, *args))
                    
    def set_mount_point (self, mount):    
        if not mount:
            self.mount_p = "/"
        elif mount [-1] != "/":
            self.mount_p = mount + "/"
        else:
            self.mount_p = mount
        self.path_suffix_len = len (self.mount_p) - 1
                
    def init (self, module, packagename = "app", mount = "/"):
        self.module = module    
        self.packagename = packagename
        self.set_mount_point (mount)
        
        if self.module:
            self.abspath = self.module.__file__
            if self.abspath [-3:] != ".py":
                self.abspath = self.abspath [:-1]
            self.update_file_info    ()
        
    def __getitem__ (self, k):
        return self.route_map [k]
    
    def get_file_info (self, module):        
        stat = os.stat (module.__file__)
        return stat.st_mtime, stat.st_size
       
    def update_file_info (self):
        stat = os.stat (self.abspath)
        self.file_info = (stat.st_mtime, stat.st_size)
        
    #------------------------------------------------------    
    @property
    def salt (self):
        if self._salt:
            return self._salt
        self._salt = self.securekey.encode ("utf8")
        return self._salt 
    
    def set_default_session_timeout (self, timeout):
        self.session_timeout = timeout
                 
    def set_devel (self, debug = True, use_reloader = True):
        self.debug = debug
        self.use_reloader = use_reloader
    
    # services management ----------------------------------------------
    PACKAGE_DIRS = ["services", "decorative"]
    CONTRIB_DIR = os.path.join (os.path.dirname (atila.__spec__.origin), 'contrib', 'services')
                
    def add_package (self, *names):
        for name in names:
            self.PACKAGE_DIRS.append (name)
    
    def _mount (self, module):
        mount_func = None
        if hasattr (module, "mount"):
            mount_func = module.mount
        elif hasattr (module, "decorate"): # for old ver
            mount_func = module.decorate
                        
        if mount_func:
            if not self.auto_mount and module not in self.mount_params:            
                return        
            params = self.mount_params.get (module, {})
            if params.get ("debug_only") and not self.debug:
                return
            # for app
            setattr (module, "__options__", params)
            setattr (module, "_mount__", params)
            # for app initialzing and reloading
            self._mount_option = params
            try:
                mount_func (self)
                self.log ("{} mounted".format (module.__name__), "info")
            finally:    
                self._mount_option = {}
                
        try:
            self.reloadables [module] = self.get_file_info (module)
        except FileNotFoundError:
            del self.reloadables [module]
            return        
        # find recursively
        self.find_mountables (module)
        
    def find_mountables (self, module):
        for attr in dir (module):
            v = getattr (module, attr)
            try:
                modpath = v.__spec__.origin
            except AttributeError:
                continue
            if not modpath:
                continue            
            if v in self.reloadables:
                continue
            if self.contrib_devel:
                if modpath.startswith (self.CONTRIB_DIR):
                    self._mount (v)
                    continue
            for package_dir in self._package_dirs:
                if modpath.startswith (package_dir):
                    self._mount (v)
                    break
    
    def add_package_dir (self, path):
        if path not in self._package_dirs:
            self._package_dirs.append (path)
            
    def mount_externals (self):
        for module in self.mount_params:            
            if module in self.reloadables:
                continue
            self._mount (module)
        
    def mount (self, maybe_point = None, *modules, **kargs):
        if maybe_point:
            if isinstance (maybe_point, str):                
                kargs ["point"] = maybe_point
            else:
                modules = (maybe_point,) + modules
        for module in modules:
            assert hasattr (module, "mount") or hasattr (module, "decorate")            
            self.add_package_dir (os.path.dirname (module.__spec__.origin))
            self.mount_params [module] = (kargs)
    mount_with = decorate_with = mount    
    
    def umount (self, *modules):
        for module in modules:
            umount_func = None
            if hasattr (module, "umount"):
                umount_func = module.umount
            elif hasattr (module, "dettach"): # for old ver
                umount_func = module.dettach 
            umount_func and umount_func (self)
            self.log ("%s umounted" % module.__name__, "info")
         
    def  umount_all (self):
        self.umount (*tuple (self.reloadables.keys ()))
    dettach_all = umount_all
    
    def maybe_reload (self):
        if time.time () - self.last_reloaded < 1.0:
            return
        
        self._reloading = True
        for module in list (self.reloadables.keys ()):
            try:
                fi = self.get_file_info (module)
            except FileNotFoundError:
                del self.reloadables [module]
                continue
                
            if self.reloadables [module] != fi:
                self.log ("reloading service, %s" % module.__name__, "info")
                self._current_function_specs = {}
                if hasattr (module, "dettach"):
                    module.dettach (self)
                with self.lock:
                    newmodule = reload (module)
                    del self.reloadables [module]
                    self._mount (newmodule)
                    
        self.load_jinja_filters ()
        self.last_reloaded = time.time ()        
        self._reloading = False
    
    def get_func_id (self,  func):
        return ("ns" in self._mount_option and self._mount_option ["ns"] + "." or "") + func.__name__     
        
    # function param saver ------------------------------------------
    def save_function_spec (self, func):
        # save original function spec for preventing distortion by decorating wrapper
        # all wrapper has *args and **karg but we want to keep original function spec for auto parametering call
        func_id = self.get_func_id (func)
        if func_id not in self._function_specs or func_id not in self._current_function_specs:
            # save origin spec
            self._function_specs [func_id] = inspect.getfullargspec(func)
            self._current_function_specs [func_id] = None
    
    def get_function_spec (self, func):        
        # called by websocet_handler 
        func_id = self.get_func_id (func)        
        return self._function_specs.get (func_id)
    
    # logger ----------------------------------------------------------
    def set_logger (self, logger):
        self.logger = logger 
        
    def log (self, msg, type = "info"):
        self.logger (msg, type)
    
    def trace (self):
        self.logger.trace ()
   
    PHASES = {
        'before_mount': 0,
        'mounted': 3,
        'before_reload': 5,
        'reloaded': 1,
        'before_umount': 4,
        'umounted': 2,
        'mounted_or_reloaded': 6
    }
    def life_cycle (self, phase, obj):
        if phase in ("umounted", "before_reload"):
            self.dettach_all ()
        index = self.PHASES.get (phase)
        func = self._binds_server [index]
        if not func:
            return        
        
        obj.app = self
        try:
            func (obj)
        except:
            if self.logger:
                self.logger.trace ()
            else:
                raise                             
    
    # Error handling ------------------------------------------------------        
    def render_error (self, error):
        handler = self.handlers.get (error ['code'], self.handlers.get (0))
        if not handler:
            return
        was = the_was._get ()    
        # reset was.app for rendering
        was.app = self
        content =    handler [0] (was, error)
        was.app = None
        return content
    
    # URL Building ------------------------------------------------
    def urlfor (self, thing, *args, **kargs):
        if isinstance (thing, FunctionType):
            thing = self._function_names [id (thing)]
        if thing.startswith ("/"):
            return self.basepath [:-1] + self.mount_p [:-1] + thing
        
        script_name_only = "__resource_path_only__" in kargs
        try:
            fpath = self._function_names [thing]
            if len (fpath) == 2:
                if not args and not kargs:
                    proto = self.route_map [fpath [0]]['__proto__']
                else:
                    proto = self.route_map_fancy [fpath [0]][fpath [1]]['__proto__']                
            else:    
                proto = self.route_map [fpath [0]]['__proto__']
        except KeyError:
            raise NameError ("{} not found".format (str (thing)))
        func, name, fuvars, favars, numvars, str_rule, options = proto
        
        if script_name_only:
            url = str_rule
            if favars:
                s = url.find ("<")
                if s != -1:
                    url = url [:s]
            return self.urlfor (url)
        
        params = {}
        try:
            currents = kargs.pop ("__defaults__")
        except KeyError:
            currents = {}
        else:
            for k, v in currents.items ():
                if k in fuvars:
                    params [k] = v
        
        if "argspec" in options:
            fuvars, favars, numvars = options ["argspec"]
            if len (args) or favars [0][0] in kargs or favars [0][0] in params:
                n, t = favars[0]
                str_rule += "/<{}{}>".format (t != "string" and (t + ":") or "", favars[0][0])
        
        function_args = options.get ("args", [])
        has_kargs = options.get ("keywords")
        
        for i in range (len (args)):
            try:
                name = function_args [i]
            except IndexError:
                raise ValueError ("too many parameters")
            params [name] = args [i]
        
        for k, v in kargs.items ():
            if not has_kargs and k not in function_args:
                raise ValueError ("parameter {} is not allowed".format (k))
            params [k] = v
        
        url = str_rule
        if favars: #fancy [(name, type),...]. /fancy/<int:cid>/<cname>
            for n, t in favars:
                if n not in params:
                    try:
                        params [n] = currents [n]
                    except KeyError:
                        try:
                            params [n] = options ["defaults"][n]                            
                        except KeyError:
                            raise AssertionError ("Argument '%s' missing" % n)
                     
                value = quote_plus (str (params [n]))
                if t == "string":
                    value = value.replace ("+", "_")
                elif t == "path":
                    value = value.replace ("%2F", "/")
                url = url.replace ("<%s%s>" % (t != "string" and t + ":" or "", n), value)
                del params [n]
        
        if params:
            url = url + "?" + "&".join (["%s=%s" % (k, quote_plus (str(v))) for k, v in params.items ()])
            
        return self.urlfor (url)
    build_url = urlfor
        
    # Routing ------------------------------------------------------                            
    def get_route_map (self):
        return self.route_map
    
    def set_route_map (self, route_map):
        self.route_map = route_map
                    
    def get_routed (self, method_chain):
        if not method_chain: 
            return
        temp = method_chain
        while 1:
            routed = temp [1]
            if type (routed) is not list:
                return routed
            temp = routed
                    
    def find_route (self, path_info, command):
        if not path_info:
            return self.urlfor ("/"), None
        if path_info in self.route_map:
            #command = command in self.route_map [path_info] and command or "__default__"            
            try: 
                proto = self.route_map [path_info][command]
            except KeyError:
                raise AssertionError            
            return proto [0], proto [-1]
        
        trydir = path_info + "/"
        if trydir in self.route_map:
            return self.urlfor (trydir), None
        raise KeyError
    
    def verify_rule (self, path_info, rule, protos, command):
        arglist = rule.findall (path_info)
        if not arglist:
            return None, None, None
        
        try:
            f, n, l, a, c, s, options = protos [command]
        except KeyError:
            raise AssertionError
        
        arglist = arglist [0]
        if type (arglist) is not tuple:
            arglist = (arglist,)
            
        kargs = {}
        for i in range (len(arglist)):
            an, at = a [i]
            if at == "int":
                kargs [an] = int (arglist [i])
            elif at == "float":
                kargs [an] = float (arglist [i])
            elif at == "path":
                kargs [an] = unquote_plus (arglist [i])
            else:        
                kargs [an] = unquote_plus (arglist [i]).replace ("_", " ")
                
        return f, options, kargs

    def find_method (self, path_info, command):
        if not (path_info.startswith (self.mount_p) or (path_info + "/").startswith (self.mount_p)):
            return self, None, None, None, 404
        
        path_info = path_info [self.path_suffix_len:]
        method, kargs = None, {}
        
        try:
            try:
                method, options = self.find_route (path_info, command)        
            except KeyError:
                for prefix, rule in self._route_priority:
                    if not path_info.startswith (prefix):
                        continue                    
                    protos = self.route_map_fancy [prefix][rule]
                    method, options, kargs = self.verify_rule (path_info, rule, protos, command)
                    if method:
                        break
        except AssertionError:
            return self, None, None, None, 405 # method not allowed     
                
        if method is None:
            return self, None, None, None, 404
        if isinstance (method, str):
            return self, method, None, None, 301
          
        return (
            self, 
            [self._binds_request [0], method] + self._binds_request [1:4], 
            kargs, 
            options, 
            None
        ) 
    
    # model signal ---------------------------------------------
    def _model_changed (self, sender, **karg):
        model_name = str (sender)[8:-2]
        karg ['x_model_class'] = model_name
        if 'created' not in karg:
            karg ["x_operation"] = 'D'
        elif karg["created"]:
            karg ["x_operation"] = 'C'
        else:
            karg ["x_operation"] = 'U'
        karg ["x_ignore"]    = True
        the_was._get ().setlu (model_name, sender, **karg)
    
    def redirect_signal (self, framework = "django"):
        if framework == "django":    
            from django.db.models.signals import post_save, post_delete        
            post_save.connect (self._model_changed)
            post_delete.connect (self._model_changed)
    model_signal = redirect_signal
    
    def remove_events (self, broad_bus):
        for (fname, event), f in self.events.items ():
            try:    
                broad_bus.remove_event (fname, event)
            except EventDoesntExist: 
                pass

    # app startup and shutdown --------------------------------------------    
    def cleanup (self):   
        pass
            
    def _start (self, wasc, route, reload = False):
        self.wasc = wasc
        if not route:
            self.basepath = "/"
        elif not route.endswith ("/"):            
            self.basepath = route + "/"
        else:
            self.basepath = route
        
    def start (self, wasc, route):
        self.bus.emit ("app:starting", wasc)
        self._start (wasc, route)
        self.bus.emit ("app:started", wasc)
        self._started = True
        
    def restart (self, wasc, route):        
        self._reloading = True
        self.bus.emit ("app:restarting", wasc)    
        self._start (wasc, route, True)
        self.bus.emit ("app:restarted", wasc)    
        self._reloading = False
    
    