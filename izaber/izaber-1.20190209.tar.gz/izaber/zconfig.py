# ==================================================
# some nice things about this class
# ==================================================

import appdirs
import os
import yaml
import re
import copy

from izaber.compat import *
from izaber.startup import initializer, app_config
from izaber.structs import DictObj, deep_merge

class YAMLConfig(object):
    _app_name = 'ZaberConfig'
    _app_author = 'Zaber'
    _config_filename = 'izaber.yaml'
    _config_dirs = [
                    appdirs.user_data_dir(_app_name, _app_author),
                    os.path.expanduser('~'),
                    '.',
                  ]
    _overlays = []

    _cfg = None
    _cfg_merged = None

    # ================================================
    # constructor
    # ================================================
    def __init__(self,*args,**kwargs):
        if args or kwargs:
            self.load_config(*args,**kwargs)

    # ================================================
    # helpers
    # ================================================
    def __repr__(self):
        """ Returns the YAML representation of the configuration
        """
        return yaml.dump(self._cfg, default_flow_style=False)

    def __nonzero__(self):
        return self._cfg or False

    def dict(self):
        return self._cfg_merged

    def config_find(self,config_dirs=None,config_filename=None):
        """ Attempt to use the config dir/config_filenames to
            locate the configuration file requested. Some folks
            would prefer to keep their config in ~ where it's in
            plain sight rather than the buried application
            specific location
        """
        if config_dirs is None:
            config_dirs = self._config_dirs
        else:
            if isinstance(config_dirs,basestring):
                config_dirs = [config_dirs]

        if config_filename is None:
            config_filename = self._config_filename
        for test_dir in config_dirs:
            test_fpath = os.path.join(test_dir,config_filename)
            if os.path.isfile(test_fpath):
                return test_fpath

        # No matches found
        return

    def load_config( self,
                  config_filename=None,
                  config_dirs=None,
                  config_buffer=None,
                  config_amend=None,
                  environment=None,
                  overlays=None,
                ):
        # Does the actual work of loading

        # Setup defaults
        if config_filename:
            self._config_filename = config_filename
        if config_dirs:
            if isinstance(config_dirs,basestring):
                self._config_dirs = [config_dirs]
            else:
                self._config_dirs = config_dirs

        if config_buffer:
            self._config_full_filname = None
            self._cfg = yaml.load(config_buffer)
        else:
            self.config_fpath = self.config_find() \
                                          or os.path.join(self._config_dirs[0], \
                                             self._config_filename)

            # check if config directory exists, and create if necessary
            self._config_dir = os.path.dirname(self.config_fpath)
            if not os.path.exists(self._config_dir):
                os.makedirs(self._config_dir)

            try:
                with open(self.config_fpath,'r') as file_obj:
                    self._cfg = yaml.load(file_obj)
            except IOError:
                self._cfg = {}

        # initialize environment
        if environment == None:
            environment = 'default'
        self._env = environment

        # Apply the overlay if required
        if not overlays:
            overlays = []
        self._overlays = overlays
        self.overlay_load()

        # Amend the configurations if required
        if config_amend:
            self.config_amend_(config_amend)

    def overlay_load(self):
        _cfg_merged = copy.deepcopy(self._cfg.get('default',{}))
        if self._env not in self._cfg:
            raise Exception("Could not find environment '%s' in configuration",self._env)
        _cfg_merged = deep_merge(_cfg_merged,self._cfg[self._env])
        for overlay in self._overlays:
            _cfg_merged = deep_merge(_cfg_merged,overlay)
        self._cfg_merged = _cfg_merged

    def overlay_add(self,overlay):
        self._overlays.append(overlay)
        self._cfg_merged = deep_merge(self._cfg_merged,overlay)

    # ================================================
    # dealing with dynamic attributes
    # ================================================
    def get(self,k,default=None):
        """ FIXME: support dot syntax here """
        return self._cfg_merged.get(k,default)

    def __getattr__(self, name):
        if name not in self._cfg_merged:
            raise AttributeError("{} is not an attribute".format(name))
        v = self._cfg_merged[name]
        if isinstance(v,dict):
            return DictObj(self,v)
        return v

    def __getitem__(self,name):
        return self.__getattr__(name)

    def addon_config(self,name):
        if name in self._cfg_merged:
            v = self._cfg_merged[name]
        else:
            v = {}
            self._cfg[self._env][name] = v
            self._cfg_merged[name] = v
        return DictObj(self,v)

    # ================================================
    # choose the environment
    # ================================================
    def environment(self, env=None):
        if env != None:
            self._env = env
            if self._env not in self._cfg:
                self._cfg[self._env] = {}
        return self._env

    # ================================================
    # Configuration Amending/Extending
    # ================================================
    def cfg_(self,cfg=None):
        """
        Getter/Setter of configuration data. This can be used
        to update and modify the configuration file on the system
        by new applications.
        """
        if cfg is None:
            cfg = self._cfg
        else:
            self._cfg = cfg
        self.overlay_load()
        return cfg

    def config_amend_key_(self,key,value):
        """ This will take a stringified key representation and value and
        load it into the configuration file for furthur usage. The good
        part about this method is that it doesn't clobber, only appends
        when keys are missing.
        """
        cfg_i = self._cfg
        keys = key.split('.')
        last_key = keys.pop()
        trail = []
        for e in keys:
            cfg_i.setdefault(e,{})
            cfg_i = cfg_i[e]
            trail.append(e)
            if not isinstance(cfg_i,dict):
                raise Exception('.'.join(trail) + ' has conflicting dict/scalar types!')
        cfg_i.setdefault(last_key,value)

    def config_amend_(self,config_amend):
        """ This will take a YAML or dict configuration and load it into
            the configuration file for furthur usage. The good part
            about this method is that it doesn't clobber, only appends
            when keys are missing.

            This should provide a value in dictionary format like:

            {
              'default': {
                'togglsync': {
                  'dsn': 'sqlite:///zerp-toggl.db',
                  'default': {
                    'username': 'abced',
                    'toggl_api_key': 'arfarfarf',
                  },
                  'dev': {
                    'cache': False
                  }
               }
            }

            OR at user's preference can also use yaml format:

            default:
              togglsync:
                  dsn: 'sqlite:///zerp-toggl.db'
                  default:
                    username: 'abced'
                    toggl_api_key: 'arfarfarf'
                  dev:
                    cache: False

            Then the code will append the key/values where they may be
            missing.

            If there is a conflict between a dict key and a value, this
            function will throw an exception.

            IMPORTANT: after making the change to the configuration, 
                       remember to save the changes with cfg.save_()

        """
        if not isinstance(config_amend,dict):
            config_amend = yaml.load(config_amend)

        def merge_dicts(source,target,breadcrumbs=None):
            """
            Function to update the configuration if required. Returns
            True if a change was made.
            """

            changed = False

            if breadcrumbs is None:
                breadcrumbs = []

            # Don't descend if we're not a dict
            if not isinstance(source,dict):
              return source

            # Let's start iterating over things
            for k,v in source.items():

                # New key, simply add.
                if k not in target:
                    target[k] = v
                    changed = True
                    continue

                # Not new key.... so is it a dict?
                elif isinstance(target[k],dict):
                    trail = breadcrumbs+[k]
                    if isinstance(v,dict):
                        if merge_dicts(v,target[k],trail):
                            changed = True
                    else:
                        raise Exception('.'.join(trail) + ' has conflicting dict/scalar types!')

                else:
                    trail = breadcrumbs+[k]
                    if isinstance(v,dict):
                        raise Exception('.'.join(trail) + ' has conflicting dict/scalar types!')

            return changed

        if merge_dicts(config_amend,self._cfg):
            self.overlay_load()

        return self._cfg


    def config_update_key_(self,key,value):
        """ This will take a stringified key representation and value and
        load it into the configuration file for furthur usage.
        This method will clobber existing entries allowing something like a
        "reset"
        """
        cfg_i = self._cfg
        keys = key.split('.')
        last_key = keys.pop()
        trail = []
        for e in keys:
            cfg_i.setdefault(e,{})
            cfg_i = cfg_i[e]
            trail.append(e)
            if not isinstance(cfg_i,dict):
                raise Exception('.'.join(trail) + ' has conflicting dict/scalar types!')
        cfg_i[last_key] = value

    def config_update_(self,config_amend):
        """ This will take a YAML or dict configuration and load it into
            the configuration file for furthur usage.
            This method will clobber existing entries allowing something like a
            "reset"

            This should provide a value in dictionary format like:

            {
              'default': {
                'togglsync': {
                  'dsn': 'sqlite:///zerp-toggl.db',
                  'default': {
                    'username': 'abced',
                    'toggl_api_key': 'arfarfarf',
                  },
                  'dev': {
                    'cache': False
                  }
               }
            }

            OR at user's preference can also use yaml format:

            default:
              togglsync:
                  dsn: 'sqlite:///zerp-toggl.db'
                  default:
                    username: 'abced'
                    toggl_api_key: 'arfarfarf'
                  dev:
                    cache: False

            Then the code will append the key/values where they may be
            missing.

            If there is a conflict between a dict key and a value, this
            function will throw an exception.

            IMPORTANT: after making the change to the configuration, 
                       remember to save the changes with cfg.save_()

        """
        if not isinstance(config_amend,dict):
            config_amend = yaml.load(config_amend)

        def merge_dicts(source,target,breadcrumbs=None):
            """
            Function to update the configuration if required. Returns
            True if a change was made.
            """

            changed = False

            if breadcrumbs is None:
                breadcrumbs = []

            # Don't descend if we're not a dict
            if not isinstance(source,dict):
              return source

            # Let's start iterating over things
            for k,v in source.items():

                # New key, simply add.
                if k not in target:
                    target[k] = v
                    changed = True
                    continue

                # Not new key.... so is it a dict?
                elif isinstance(target[k],dict):
                    trail = breadcrumbs+[k]
                    if isinstance(v,dict):
                        if merge_dicts(v,target[k],trail):
                            changed = True
                    else:
                        raise Exception('.'.join(trail) + ' has conflicting dict/scalar types!')

                else:
                    trail = breadcrumbs+[k]
                    if isinstance(v,dict):
                        raise Exception('.'.join(trail) + ' has conflicting dict/scalar types!')

            return changed

        if merge_dicts(config_amend,self._cfg):
            self.overlay_load()

        return self._cfg


    # ================================================
    # write config to yaml file
    # ================================================
    def save_(self):
        if self.config_fpath == None:
            raise Exception("Cannot save config when ")
        file_obj = open(self.config_fpath, 'w')
        yaml.dump(self._cfg, file_obj, default_flow_style=False)
        file_obj.close()
        return self.config_fpath

# Global shared YAML configuration
config = YAMLConfig()

@initializer('config')
def initialize(**kwargs):
    """
    Loads the globally shared YAML configuration
    """
    global config
    config_opts = kwargs.setdefault('config',{})

    if isinstance(config_opts,basestring):
        config_opts = {'config_filename':config_opts}
        kwargs['config'] = config_opts

    if 'environment' in kwargs:
        config_opts['environment'] = kwargs['environment']

    config.load_config(**config_opts)

    # Overlay the subconfig
    if kwargs.get('name'):
        subconfig = config.get(kwargs.get('name'),{})
        config.overlay_add(subconfig)

    config.overlay_add(app_config)

