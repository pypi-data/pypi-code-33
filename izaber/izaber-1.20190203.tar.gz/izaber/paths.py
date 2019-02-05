# -*- coding: utf-8 -*-

import os
import re
import datetime
import logging

import jinja2

from izaber.compat import *

from izaber.startup import initializer, request_initialize, app_config
from izaber import config

def parse(template,**tags):
    now = datetime.datetime.now()
    tags.update({
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'dt': now.strftime('%Y-%m-%d_%H-%M-%S'),
    })
    path = jinja2.Template(template).render(**tags)
    return os.path.expanduser(path)

class Path(object):
    path_template = None
    tags = None
    path = None

    def __init__(self,path_template,**tags):
        if isinstance(path_template,Path):
            self.path_template = path_template.path_template
        else:
            self.path_template = path_template
        self.tags = tags
        self.path = self.parse(self.path_template or '.')

    def parse(self,buf,**tags):
        tags.update(self.tags)
        return parse(buf,**tags)

    def file_fpath(self,fpath,**tags):
        parsed_fpath = self.parse(fpath,**tags)
        full_fpath = os.path.join(unicode(self.path),parsed_fpath)
        return full_fpath

    def open(self,fpath,*args,**kwargs):
        return File(self.path_template,fpath).open(*args,**kwargs)

    def exists(self):
        return os.path.exists(self.path)

    def makedirs(self):
        return os.makedirs(self.path)

    def __str__(self):
        return self.path

    def __unicode__(self):
        return self.path

    def walk(self,visit,arg):
        os.path.walk(self.path,visit,arg)

class File(Path):
    full_fpath = ''
    file_handle = None

    def __init__(self,path_template,fpath,**tags):
        super(File,self).__init__(path_template,**tags)
        self.full_fpath = self.file_fpath(fpath)

    def __str__(self):
        return self.full_fpath

    def __unicode__(self):
        return self.full_fpath

    def open(self,*args,**kwargs):
        self.file_handle = open(self.full_fpath,*args,**kwargs)
        return self

    def __getattr__(self,k):
        return getattr(self.file_handle,k)

class DataDir(object):

    def __init__(self,*args,**kwargs):
        if args or kwargs:
            self.initialize(*args, **kwargs)

    def initialize(self,path=None,**kwargs):

        # Get the initial information
        path_templates = {}
        tags = {'path':path}
        for k,v in kwargs.items():
            if re.search('_path$',k):
                path_templates[k] = v
            else:
                tags[k] = v

        # Then get the base path
        self.path = Path(path,**kwargs)

        resolved_paths = {
            'path': self.path
        }
        seen = {}
        class SneakyString(object):
            def __init__(self,path_key,path_template):
                self.path_key = path_key
                self.path_template = path_template

            def path_tag(self,k,path_template,seen=None):
                if not seen: seen = {}
                if k in seen:
                    raise Exception('Cyclic dependancy found')
                if not k in resolved_paths:
                    full_path = parse(path_template,**tags)
                    resolved_paths[k] = Path(full_path,**tags)
                return resolved_paths[k]

            def __unicode__(self):
                return unicode(self.path_tag(self.path_key,self.path_template))

            def __str__(self):
                return str(self.path_tag(self.path_key,self.path_template))

        for k,path_template in path_templates.items():
            tags[k] = SneakyString(k,path_template)

        for k,path_template in path_templates.items():
            if k in resolved_paths: continue
            full_path = parse(path_template,**tags)
            resolved_paths[k] = Path(full_path,**tags)

        self.path_templates = path_templates
        self.tags = tags
        self.paths = resolved_paths

        # If any of the data directories need to be made, 
        # go ahead and do so
        for k,path in self.paths.items():
            if not path.exists():
                path.makedirs()

    def full_fpath(self,fpath,**kwargs):
        tags = dict(self.tags)
        tags.update(self.paths)
        tags.update(kwargs)
        return parse(fpath,**tags)

    def file_get(self, fname,**kwargs):
        return File(
                    fpath=fname,
                    path_template=self.path,
                    **kwargs
                )

    def path_get(self, path_template, **kwargs):
        return Path(
                    path_template=path_template,
                    **kwargs
                )

    def logger(self,fpath=None,log_level=None):
        """ Creates a custom logger
        """
        log = logging.getLogger(fpath)
        pass

    def open(self,fname,mode=None,*args,**kwargs):
        f = self.file_get(fname,**kwargs).open(mode=mode)
        return f

    def __getattr__(self,k):
        if self.paths and k in self.paths:
            return self.paths[k]
        raise AttributeError("{} is not found in {}".format(k,self.paths))

paths = DataDir()

logger_defaults = {
  'filemode': 'a',
  # 'format': '%(levelname)s %(asctime)s %(module)s: %(message)s',
  'datefmt': '%Y-%m-%d %H:%M:%S',
  'level': logging.WARNING
}

class Logger(logging.Logger):

    _iz_filename = None
    _iz_handler = None
    _iz_format = None
    _iz_name = None

    def __init__(self,name=None,**kwargs):
        super(Logger,self).__init__(name)
        self._iz_name = name
        if kwargs:
            self.init(**kwargs)

    def init(self,**kwargs):

        # Load the gloabl config if any
        log_config = dict(logger_defaults)
        log_config.update(config.get('log',{}))
        log_config.update(app_config.get('log',{}))
        log_config.update(config.get('log',{}).get(self._iz_name,{}))
        log_config.update(app_config.get('log',{}).get(self._iz_name,{}))
        log_config.update(kwargs)

        if log_config.get('level') and self._iz_handler:
            self._iz_handler.setLevel(log_config['level'])

        if log_config.get('filename') and not self._iz_filename:
            filename = paths.full_fpath(log_config['filename'])
            self._iz_handler = logging.FileHandler(
                                    filename=filename,
                                    mode=log_config.get('filemode','a'),
                                    encoding=log_config.get('fileencoding','utf8'),
                                )
            self._iz_handler.setLevel(logging.DEBUG)
            self.addHandler(self._iz_handler)

        if log_config.get('formatter') and self._iz_handler:
            self._iz_format = log_config['formatter']
            self._iz_handler.setFormatter(log_config['formatter'])

        if log_config.get('format') and not self._iz_format:
            formatter = logging.Formatter(
                fmt=log_config['format'],
                datefmt=log_config.get('dateformat'),
            )
            self._iz_handler.setFormatter(formatter)
            self._iz_format = log_config.get('format')

        if log_config.get('level') and self._iz_handler:
            self._iz_handler.setLevel(log_config['level'])

logging.setLoggerClass(Logger)

log = logging.getLogger()

def getLogger(name,**kwargs):
    log = logging.getLogger(name)
    log.init(**kwargs)
    return log

@initializer('paths')
def initialize(**kwargs):

    request_initialize('config',**kwargs)

    # Setup the paths
    # Path configuration should be in the format:
    # paths: {
    #     path: path to main data directory
    #
    #     custom_path1: encoded path
    #     ...
    #     custom_pathN: encoded path
    #
    # }

    # Setup the paths first
    paths_config = config.get('paths',{})
    paths_config.update(kwargs.get('paths',{}))
    if 'path' not in paths_config:
        for path_location in ['/tmp','/temp','.']:
            if os.path.isdir(path_location):
                paths_config.setdefault('path',path_location)
                break
    paths.initialize(**paths_config)

    # Setup the logger
    # Log configuration should be in the format:
    # log: {
    #     filename: paths compatible filepath
    #     filemode: usually 'a'
    #     fileencoding: usually 'utf8'
    #     format: logs formatter compatible format
    #     dateformat: how to display dates
    #     level: filter out everything above this level
    #
    #     custom_logger_name1: {
    #         filename: paths compatible filepath
    #         filemode: usually 'a'
    #         fileencoding: usually 'utf8'
    #         format: logs formatter compatible format
    #         dateformat: how to display dates
    #         level: filter out everything above this level
    #     },
    #     ...
    #     custom_logger_nameN: {
    #         filename: paths compatible filepath
    #         filemode: usually 'a'
    #         fileencoding: usually 'utf8'
    #         format: logs formatter compatible format
    #         dateformat: how to display dates
    #         level: filter out everything above this level
    #     },
    # }
    #
    log_config = dict(logger_defaults)
    log_config.update(config.get('log',{}))
    log_config.update(kwargs.get('log',{}))

    # Default to app_dir/izaber.log if path not defined
    filename = paths.file_get('izaber.log')
    log_config.setdefault('filename',unicode(filename))
    log_config['filename'] = paths.full_fpath(log_config['filename'])

    logging.basicConfig(**log_config)
    logging.getLogger().addHandler(logging.StreamHandler())

