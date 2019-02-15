import os
from . import appbase, multipart_collector, cookie, session, grpc_collector, ws_executor
from . import wsgi_executor, xmlrpc_executor, grpc_executor, jsonrpc_executor
from aquests.protocols.grpc import discover
from sqlphile import Template, DB_PGSQL
from skitai.wsgi_apps import Config
import skitai
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
        
class Atila (appbase.AppBase):
    templates_dirs = []
    PRESERVES_ON_RELOAD = ["reloadables"]
    
    def __init__ (self, app_name):
        appbase.AppBase.__init__ (self)
        self.app_name = app_name
        self.home = None
        self.jinja_env = None        
        self.chameleon = None
        self.sqlphile = None
        # for bus, set by wsgi_executor        
        self.config = Config (preset = True)
        self._aliases = []
        self._sqlmap_dir = None
        self._jinja2_patch_options = None        
        
    #--------------------------------------------------------
                
    def alias (self, *args, **karg):
        name, args = skitai.alias (*args, **karg)                
        skitai.dconf ["clusters"].pop (name)
        ctype, members, policy, ssl = args
        self._aliases.append ((ctype, "{}:{}".format (name, self.app_name), members, ssl, policy))
        
    def test_client (self, point = "/", approot = ".", numthreads = 1):
        from skitai import testutil
        from skitai.testutil import client    
        
        class Client (client.Client):        
            def make_request (self, *args, **karg):
                request = client.Client.make_request (self, *args, **karg)
                return self.handle_request (request)
                
            def __enter__ (self):
                return self
                
            def __exit__ (self, type, value, tb):
                pass
                     
        testutil.activate ()
        testutil.install_vhost_handler ()        
        testutil.mount (point, (self, approot))
        return Client ()
    
    # template engine -----------------------------------------------        
    def skito_jinja (self, option = 0):
        if option == 0:    
            self.jinja_overlay ("${", "}", "<%", "%>", "<!---", "--->")
        elif option == 1:
            self.jinja_overlay ("${", "}", "{%", "%}", "{#", "#}")
        elif option == 2:
            self.jinja_overlay ("{*", "*}", "{%", "%}", "{#", "#}")    
        elif option == 3:
            self.jinja_overlay ("{#", "#}", "{%", "%}", "<!---", "--->")        
        elif option == 4:
            self.jinja_overlay ("##", "##", "{%", "%}", "<!---", "--->")            
        elif option == 5:
            self.jinja_overlay ("{:", ":}", "{%", "%}", "<!---", "--->")                
        elif option == 6:
            self.jinja_overlay ("<%", "%>", "{%", "%}", "<!---", "--->")                    
        elif option == 7:
            self.jinja_overlay ("{%", "%}", "<%", "%>", "<!---", "--->")
        
    def jinja_overlay (
        self, 
        variable_start_string = "{{",
        variable_end_string = "}}", 
        block_start_string = "{%", 
        block_end_string = "%}", 
        comment_start_string = "{#",
        comment_end_string = "#}",
        line_statement_prefix = "%", 
        line_comment_prefix = "%%",
        **karg
    ):
        # delay before app is actual imported
        self._jinja2_patch_options = (
            variable_start_string, variable_end_string, block_start_string, block_end_string, 
            comment_start_string, comment_end_string, line_statement_prefix, line_comment_prefix, 
            karg
        )
    
    def _jinja_overlay (self):    
        from .patches import jinjapatch
        self.jinja_env = jinjapatch.overlay (
            self.app_name, 
            *self._jinja2_patch_options [:-1], 
            **self._jinja2_patch_options [-1]
        )
        
    def render (self, was, template_file, _do_not_use_this_variable_name_ = {}, **karg):
        while template_file and template_file [0] == "/":
            template_file = template_file [1:]    

        if _do_not_use_this_variable_name_: 
            assert not karg, "Can't Use Dictionary and Keyword Args Both"
            karg = _do_not_use_this_variable_name_

        karg ["was"] = was
        karg.update (self._template_globals)
        
        template = self.get_template (template_file)
        self.emit ("template:rendering", template, karg)
        rendered = template.render (**karg)
        self.emit ("template:rendered", rendered)
        return rendered
                    
    def get_template (self, name):
        if name.endswith ('.pt') or name.endswith (".ptal"):
            if self.chameleon is None:
                raise SystemError ('Chameleon template engine is not installed')
            return self.chameleon [name]
        return self.jinja_env.get_template (name)        
    
    def get_template_loader (self):
        templates = [FileSystemLoader (os.path.join (self.home, "templates"))]
        for tdir in self.templates_dirs:
            templates.append (FileSystemLoader (tdir))
        templates.append (FileSystemLoader(os.path.join (os.path.dirname (__file__), 'contrib', 'templates')))                
        return ChoiceLoader (templates)
    
    # directory management ----------------------------------------------------------    
    def set_home (self, path, module = None):
        self.home = path
        
        # for backward competable
        if self.authenticate is True:            
            try:
                self.authenticate = self.authorization
            except AttributeError:     
                self.authenticate = "digest"
        
        # configure jinja --------------------------------------------
        if self._jinja2_patch_options:
            self._jinja_overlay ()
        loader = self.get_template_loader ()
        if self.jinja_env:
            # activated skito_jinja
            self.jinja_env.loader = loader
        else:
            self.jinja_env = Environment (loader = loader)
        
        # chameleon -------------------------------------
        try: from chameleon import PageTemplateLoader
        except: pass        
        else:        
            self.chameleon = PageTemplateLoader (
                os.path.join(path, "templates"),
                auto_reload = self.use_reloader,
                restricted_namespace = False
            )
            
        # unbinded sqlphile --------------------------------------------
        self.initialize_sqlphile (path)
        
        # vaild packages --------------------------------------------
        for d in self.PACKAGE_DIRS:
            maybe_dir = os.path.join (path, d)
            if os.path.isdir (maybe_dir):
                self.add_package_dir (maybe_dir)
                
        if module:
            self.find_mountables (module)
        self.mount_externals () # these're not auto reloadad
        self.load_jinja_filters ()
            
    def load_jinja_filters (self):    
        for k, v in self._jinja2_filters.items ():
            self.jinja_env.filters [k] = v
        self._jinja2_filters = {}
        
    def setup_sqlphile (self, engine, template_dir = "sqlmaps"):
        self.config.sql_engine = engine
        self.config.sqlmap_dir = template_dir
    
    def initialize_sqlphile (self, path):
        self._sqlmap_dir = os.path.join(path, self.config.get ("sqlmap_dir", "sqlmaps"))
        if not os.path.isdir (self._sqlmap_dir):
            self._sqlmap_dir = None
        self.sqlphile = Template (self.config.get ("sql_engine", DB_PGSQL), self._sqlmap_dir, self.use_reloader)
    
    def get_collector (self, request):
        ct = request.get_header ("content-type")
        if not ct: return
        if ct.startswith ("multipart/form-data"):
            return multipart_collector.MultipartCollector
            
        if ct.startswith ("application/grpc"):
            try:
                i, o = discover.find_type (request.uri [1:])
            except KeyError:
                raise NotImplementedError            
            return grpc_collector.grpc_collector            
    
    # method search -------------------------------------------
    def get_method (self, path_info, request):
        command = request.command.upper ()
        content_type = request.get_header_noparam ('content-type')
        current_app, method, kargs = self, None, {}
        
        if self.use_reloader:
            with self.lock:
                self.maybe_reload ()
                current_app, method, kargs, options, status_code = self.find_method (path_info, command)
        else:
            current_app, method, kargs, options, status_code = self.find_method (path_info, command)
        
        if status_code:
            return current_app, method, kargs, options, status_code

        status_code = 0
        if options:
            allowed_types = options.get ("content_types", [])
            if allowed_types and content_type not in allowed_types:
                return current_app, None, None, options, 415 # unsupported media type
            
            if command == "OPTIONS":								
                allowed_methods = options.get ("methods", [])
                request_method = request.get_header ("Access-Control-Request-Method")
                if request_method and request_method not in allowed_methods:
                    return current_app, None, None, options, 405 # method not allowed
            
                response = request.response
                response.set_header ("Access-Control-Allow-Methods", ", ".join (allowed_methods))
                access_control_max_age = options.get ("access_control_max_age", self.access_control_max_age)    
                if access_control_max_age:
                    response.set_header ("Access-Control-Max-Age", str (access_control_max_age))
                
                requeste_headers = request.get_header ("Access-Control-Request-Headers", "")        
                if requeste_headers:
                    response.set_header ("Access-Control-Allow-Headers", requeste_headers)                    
                status_code = 200
            
            else:
                if not self.is_allowed_origin (request, options.get ("access_control_allow_origin", self.access_control_allow_origin)):
                    status_code =  403
                elif not self.is_authorized (request, options.get ("authenticate", self.authenticate)):
                    status_code =  401
        
        if status_code in (401, 200):
            authenticate = options.get ("authenticate", self.authenticate)
            if authenticate:
                request.response.set_header ("Access-Control-Allow-Credentials", "true")
                            
        access_control_allow_origin = options.get ("access_control_allow_origin", self.access_control_allow_origin)
        if access_control_allow_origin and access_control_allow_origin != 'same':
            request.response.set_header ("Access-Control-Allow-Origin", ", ".join (access_control_allow_origin))
        
        return current_app, method, kargs, options, status_code
    
    #------------------------------------------------------
    def create_on_demand (self, was, name):
        class G: 
            pass
        
        # create just in time objects
        if name == "cookie":
            return cookie.Cookie (was.request, self.securekey, self.basepath [:-1], self.session_timeout)
            
        elif name in ("session", "mbox"):
            if not was.in__dict__ ("cookie"):
                was.cookie = cookie.Cookie (was.request, self.securekey, self.basepath [:-1], self.session_timeout)            
            if name == "session":
                return was.cookie.get_session ()
            if name == "mbox":
                return was.cookie.get_notices ()
                
        elif name == "g":
            return G ()
        
    def cleanup_on_demands (self, was):
        if was.in__dict__ ("g"):
            del was.g
        if not was.in__dict__ ("cookie"):
            return
        for j in ("session", "mbox"):
            if was.in__dict__ (j):        
                delattr (was, j)
        del was.cookie
                                        
    def __call__ (self, env, start_response):
        was = env ["skitai.was"]        
        was.app = self        
        was.response = was.request.response
        
        content_type = env.get ("CONTENT_TYPE", "")                
        if content_type.startswith ("text/xml") or content_type.startswith ("application/xml"):
            result = xmlrpc_executor.Executor (env, self.get_method) ()
        elif content_type.startswith ("application/grpc"):
            result = grpc_executor.Executor (env, self.get_method) ()            
        elif content_type.startswith ("application/json-rpc"):
            result = jsonrpc_executor.Executor (env, self.get_method) ()    
        elif env.get ("websocket.params"):
            result = ws_executor.Executor (env, None) ()
        else:    
            result = wsgi_executor.Executor (env, self.get_method) ()
    
        self.cleanup_on_demands (was) # del session, mbox, cookie, g
        del was.response        
        was.app = None        
        return result
        