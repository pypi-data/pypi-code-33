'''
:Date: 2019-01-30
:Version: 0.0.3
:Authors:
    * Mohammad Alghafli <thebsom@gmail.com>

cofan is an http server library for serving files and any other things. You use
it to share content in the form of a website. The current classes give you the
following:
    
    * Serve the content of a local directory in a form similar to file browser
      with icons for directories and files based on their extension.
    * Serve the content of a local zip file the same way as the local
      directories.
    * List the content of a local directory in json form.
    * Serve local html files as a web site.
    * Organize your urls in prefix trees.
    * Response differently for different ip addresses

It also supports requests of partial files to resume previously interrupted
download.

Here is an example of how to use it::
    
    from cofan import *
    import pathlib
    
    #our site will be like this:
    #   /           (this is our root. will list all the branches below)
    #   |
    #   |- vid/
    #   |  this branch is a file browser for videos
    #   |
    #   -- site/
    #      this will be a web site. just a collection of html files
    
    #lets make an http file browser and share our videos
    #first, we specify the icons used in the file browser
    #you can omit the theme. it defaults to `humanity`
    icons = Iconer(theme='humanity')
    
    #now we create a Filer and specify the path we want to serve
    vid = Filer(pathlib.Path.home() / 'Videos', iconer=icons)
    
    #we also want to serve a web site. lets create another filer. since the root
    #directory of the site contains `index.html` file, the filer
    #will automatically redirect to it instead of showing a file browser
    #no file browser also means we do not need to specify `iconer`
    #parameter. you can still use it if you want but that would not be very
    #useful
    site = Filer(pathlib.Path.home() / 'mysite')
    
    #now we need to give prefixes to our branches
    #we create a patterner
    patterns = Patterner()
    
    #then we add the iconer, filers with their prefixes
    #make sure to add a trailing slash
    patterns.add('vid/', vid)
    patterns.add('site/', site)
    #we also need to add our iconer
    #you need to tell the iconer about its prefix. by default it assumes
    #`__icons__`
    patterns.add('__icons__/', icons)
    
    #now we have all branches. but what if the user types our root url?
    #the path we will get will be an empty string which is not a prefix of any
    #branch. that will be a 404
    #lets make the root list and other branches added to `patterns`
    #the branches will be shown like the file browser but now the icons will be
    #for the patterns instead of file extensions
    #we need to specify where the icons are taken from
    #the icons file should contain an icon named `vid.<ext>` and an icon named
    #`site.<ext>` where <ext> can be any extension.
    root = PatternLister(patterns, root=pathlib.Path.home() / 'icons.zip')
    
    #and we add our root to the patterns with empty prefix
    patterns.add('', root)
    
    #now we create our handler like in http.server. we give it our patterner
    handler = BaseHandler(patterns)
    
    #and create our server like in http.server
    srv = Server(('localhost', 8000), handler)
    
    #and serve forever
    srv.serve_forever()
    
    #now try to open your browser on http://localhost:8000/

This module can also be run as a main python script to serve files from a
directory.

commandline syntax::

    python -m cofan.py [-a <addr>] [<root>]

options:

    * -a <addr>, --addr <addr>: specify the address and port to bind to. <addr>
      should be in the form `<ip>:<port>` where `<ip>` is the ip address and
      `<port>` is the tcp port. defaults to `localhost:8000`.

args:

    * root: The root directory to serve. Defaults to the current directory.
'''

import logging
import re
import pathlib
import urllib.parse
import io
import mimetypes
import http
import http.server
import socketserver
import json
import zipfile
import traceback
import datetime
try:
    from fileslice import Slicer
except ImportError:
    Slicer = None

__version__ = re.search(
        ':Version: (?P<version>[0-9](\.[0-9])*)',
        __doc__
    ).group(1)

logger = logging.getLogger(__name__)

class BaseProvider:
    '''
    basic provider class. each time a request is intended to this provider,
    the provider should return a response code, headers and body. it defines two
    methods:
        
        * get_content(): this should return the response code, headers and body
        * short_response(): helper method to send a response code and its
          description.
    
    You probably want to use one of `BaseProvider` subclasses or inherit it in
    your own class.
    '''
    @classmethod
    def get_content(self, handler, url, query=dict(), full_url=''):
        '''
        This method is called by the `http.server.BaseHTTPRequestHandler` object
        when a request arrives. It must returns a tuple containing:
        
            * Response code
            * Response headers
            * Response body
            * Postprocessing callable
        
        The response code should be an integer or a member of http.HTTPStatus.
        Response headers should be a dictionary where keys are header keywords
        and values are header values. The body must be a readable file like
        object. Postprocessing callable is a callable object which takes no
        arguments. It is called after the request is served. The body object is
        closed automatically after serving the request and does not need to be
        closed in the postprocessing callable.
        
        This method should be overridden in subclasses. The default
        implementation is to send OK response code with a body that contains
        short description of the response code.
        
        args:
        
            * handler (`http.server.BaseHTTPRequestHandler`): The object that
              called this method.
            * url (str): The url that was requested after removing all prefixes
              by other providers. Look at `Patterner` for information of how
              prefixes are stripped.
            * query (dict): Request query arguments. Defaults to empty
              dictionary.
            * full_url (str): The full url that was requested without removing
              prefixes. Defaults to empty string
        
        returns:
        
            * response (http.HTTPStatus): Response code.
            * headers (dict): Response headers.
            * content (binary file-like object): The response content.
            * postproc (callable): A callable that will be called after
              serving the content. This callable will be called as long as
              the `get_content()` method succeded regardless whether sending
              the content to the client succeded or not. The intention of
              this callable is to close all files other than `content` in
              case there are open files. For example, if `content` is a file
              inside a zip file, closing `content` is not enough without
              closing the parent zip file.
        '''
        return self.short_response()
    
    @staticmethod
    def short_response(response=http.HTTPStatus.OK, body=None):
        '''
        Convinience method which can be used to send a status code and its
        description. It returns the same values as `get_content` but the code is
        specified as a parameter and the body defaults to a description of the
        code.
              
        args:
        
            * response (http.HTTPStatus): Response code to send. Defaults to
              `http.HTTPStatus.OK`.
            * body: The value to send in the body. It defaults to `None` which
              sends a short description of the code. If the body is not a bytes
              object, it is converted to a string and then encoded to utf8.
        
        returns:
        
            * response (http.HTTPStatus): Response code given in the args.
            * headers (dict): Response headers dict with `text/html` in
              `Content-Type` header and the length of the body in
              `Content-Length` header.
            * content (binary file-like object): Description of `response` as a
              utf-8 encoded string if `body` arg is `None`. Otherwise, returns
              `body` represented as utf-8 encoded string.
            * postproc: Always a value of `None`.
        '''
        
        if body is None:
            body = '{} {}'.format(response.value, response.name.replace('_', ' ')).encode('utf8')
        elif type(body) is not bytes:
            body = str(body).encode('utf8')
        
        f = io.BytesIO(body)
        length = f.seek(0, 2)
        f.seek(0)
        headers = {
                'Content-Type':'text/html',
                'Content-Length': length,
            }
        return response, headers, f, lambda: None

class Statuser(BaseProvider):
    '''
    A subclass of `BaseProvider`. This provider is very similar to BaseProvider.
    The only difference is that it takes the response code in its constructor
    and sends this response code instead of OK.
    '''
    def __init__(self, response=http.HTTPStatus.NOT_FOUND):
        '''
        args:
        
            * response (http.HTTPStatus): The response code to send when
              `get_content()` is called. It defaults to NOT_FOUND.
        '''
        self.response = response
    def get_content(self, handler, url, query=dict(), full_url=''):
        return self.short_response(self.response)

class Patterner(BaseProvider):
    '''
    `BaseProvider` subclass that relays requests to other providers based on
    requested url pattern. The other providers are added to the `Patterner`
    instance with the request url pattern they should get. When the `Patterner`
    gets a request, it searches for a pattern that matches the beginning of the
    url. When found, the `Patterner` calls `get_content()` method of the target
    provider, giving it the same parameters but with the prefix stripped from
    the beginning of the url.
    '''
    def __init__(self):
        self.patterns = []
        self.titles = []
    
    def add(self, pattern, provider, title=''):
        '''
        Adds a pattern and a provider to the `Patterner`.
        
        args:
        
            * pattern (str): A string containing the url prefix of the provider.
            * provider (`BaseProvider`): The provider to relay the request to.
        '''
        self.patterns.append((re.compile(pattern), provider))
        self.titles.append((pattern, title))
    
    def remove(self, pattern):
        '''
        Removes a pattern and its provider from the pattern list. If a pattern
        exists multiple times (which you should not do anyway), only the first
        occurance is removed.
        
        args:
            pattern (str): Pattern to remove.
        '''
        for c in range(len(self.patterns)):
            if self.patterns[c][0].pattern == pattern:
                self.patterns.pop(c)
        else:
            raise ValueError('pattern not found')
        
        for c in range(len(self.titles)):
            if self.titles[c][0] == pattern:
                self.patterns.pop(c)
        
    def get_content(self, handler, url, query=dict(), full_url=''):
        '''
        Searches the pattern list for a pattern that matches the beginning of
        the url and relays the request to the corresponding provider. If not
        found, sends a `NOT FOUND` response.
        The search is done from the first added pattern. If two patterns
        overlap, the more specific pattern should be added first. For example,
        `files/mysite/` should be added before `files/`. Otherwise, any request
        to `files/mysite/` will be served by `files/` since it will be checked
        first.
        '''
        try:
            for pattern, provider in self.patterns:
                if pattern.match(url):
                    new_url = pattern.sub('', url, count=1)
                    return provider.get_content(handler, new_url, query, full_url)
            else:
                return self.short_response(http.HTTPStatus.NOT_FOUND)
        except Exception as e:
            logger.warning('exception in {}'.format(type(self).__name__))
            logger.warning(traceback.format_exc())
            return self.short_response(http.HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def get_patterns(self):
        '''
        Returns the pattern strings added to the `Patterner`.
        '''
        patterns = []
        for c in self.patterns:
            patterns.append(c[0].pattern)
        return patterns
    
    def get_title(self, pattern):
        '''
        Returns the pattern title.
        
        args:
        
            * pattern (str): the pattern to look for its title.
        
        returns:
        
            The pattern title.
        '''
        
        for c in range(len(self.titles)):
            if self.titles[c][0] == pattern:
                return self.titles[c][1]

class IPPatterner(Patterner):
    '''
    The same as `Patterner` but relays requests based on IP address patterns
    instead of url.
    '''
    def get_content(self, handler, url, query=dict(), full_url=''):
        try:
            addr = handler.client_address[0]
            for pattern, provider in self.patterns:
                if pattern.match(addr):
                    return provider.get_content(handler, url, query, full_url)
            else:
                return self.short_response(http.HTTPStatus.UNAUTHORIZED)
        except Exception as e:
            logger.warning('exception in {}'.format(type(self).__name__))
            logger.warning(traceback.format_exc())
            return self.short_response(http.HTTPStatus.INTERNAL_SERVER_ERROR)

class JFiler(BaseProvider):
    '''
    Lists directory contents and serves files from local file system based on
    the recieved url.
    '''
    
    HTTP_DATE_TEMPLATE = '%a, %d %b %Y %H:%M:%S GMT'
    MAX_AGE = 'max-age={}'.format(60)
    
    def __init__(self, root):
        '''
        args:
        
            * root (path-like object): Root directory or file to serve. Any
              requested url will be served starting from this directory.
        '''
        self.root = str(pathlib.Path(root).resolve())
    
    def get_content(self, handler, url, query=dict(), full_url=''):
        '''
        Serves files based on the url given starting from the `self.root`. If
        the url points to a file, the file is served. `Last-Modified` header is
        sent to help clients cache the file. If the url points to a directory,
        a list of files it contains is served as a JSON object with 2 members:
        
            * dirs: List of directories under the requested directory. If
              `full_url` parameter is not an empty string, a '..' value is
              added to the dirs list. 
            * files: List of files under the requested directory.
        
        If the url does not point to a file or directory under `self.root`, it
        responds with NOT FOUND.
        '''
        try:
            if self.is_dir(url):
                return self.serve_dir(handler, url, full_url=full_url)
            elif self.is_file(url):
                return self.serve_file(handler, url, full_url=full_url)
            else:
                return self.short_response(http.HTTPStatus.NOT_FOUND)
        except Exception as e:
            logger.warning('exception in {}'.format(type(self).__name__))
            logger.warning(traceback.format_exc())
            return self.short_response(http.HTTPStatus.INTERNAL_SERVER_ERROR)
            
    def serve_dir(self, handler, url, query=dict(), full_url=''):
        '''
        Called by `self.get_content()` when the url points to a direcotry. Gets
        a list of directories and files under the requested directory pointed by
        `url` argument.
        
        Takes the same arguments as `self.get_content()`.
        '''
        dir_ls = self.get_file_list(url, parent=bool(full_url))
        
        page = json.dumps(dir_ls)
        f = io.BytesIO(page.encode('utf8'))
        
        response = http.HTTPStatus.OK
        length = f.seek(0, 2)
        f.seek(0)
        headers = {
                'Content-Type':'application/json',
                'Content-Length': length,
            }
        
        return response, headers, f, lambda: None
    
    def serve_file(self, handler, url, query=dict(), full_url=''):
        '''
        Called by `self.get_content()` when the url points to a file. Serves the
        file content as a JSON object.
        
        Takes the same arguments as `self.get_content()`.
        '''
        path = pathlib.Path(self.root) / url
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        ifmod = handler.headers['If-Modified-Since']
        if ifmod is not None:
            ifmod = datetime.datetime.strptime(ifmod, self.HTTP_DATE_TEMPLATE)
            if mtime <= ifmod:
                response = http.HTTPStatus.NOT_MODIFIED
                headers = {}
                f = io.BytesIO(b'')
                return response, headers, f, lambda: None
        
        mime = mimetypes.guess_type(url)[0]
        f = path.open('br')
        
        response = http.HTTPStatus.OK
        length = f.seek(0, 2)
        f.seek(0)
        headers = {
                'Content-Length': length,
                'Last-Modified': mtime.strftime(self.HTTP_DATE_TEMPLATE),
                'Cache-Control': self.MAX_AGE,
            }
        if mime is not None:
            headers['Content-Type'] = mime
        
        return response, headers, f, lambda: None
    
    def exists(self, url):
        '''
        Returns `True` if the url points to an existing file or directory under
        `self.root`. Otherwise returns `False`.
        
        args:
        
            * url (path-like object): The recieved url to check.
        
        returns: True if `url` is an existing file or subdirectory in
            `self.root`. False otherwise.
        '''
        try:
            root = pathlib.Path(self.root)
            path = root / url
            path = path.resolve()
            if path.samefile(self.root) or root in path.parents:
                return path.exists()
        except FileNotFoundError:
            pass
        
        return False
    
    def is_dir(self, url):
        '''
        Returns `True` if the url points to an existing directory under
        `self.root`. Otherwise returns `False`.
        
        args:
        
            * url (path-like object): The recieved url to check.
        
        return: True if `url` is an existing subdirectory of `self.root`. False
            otherwise.
        '''
        return self.exists(url) and (pathlib.Path(self.root) / url).is_dir()
    
    def is_file(self, url):
        '''
        Returns `True` if the url points to an existing file under `self.root`.
        Otherwise returns `False`.
        
        args:
        
            * url (path-like object): The recieved url to check.
        
        returns: True if `url` is an existing file in `self.root` or one of its
            subdirectories. False otherwise.
        '''
        return self.exists(url) and (pathlib.Path(self.root) / url).is_file()
    
    def get_file_list(self, url, parent=False):
        '''
        Called by `self.get_content`. Returns a dictionary containing 2
        members:
        
            * dirs: A list of directories under the directory pointed by url.
            * files: A list of files under the directory pointed by url.
        
        args:
        
            * url (path-like object): The directory url to list its content.
            * parent (bool): If `True`, adds '..' to the dirs list. Defaults to
              False.
        '''
        if self.is_dir(url):
            path = pathlib.Path(self.root) / url
            dir_ls = [x for x in path.glob('*') if not x.name.startswith('.')]
            if parent:
                dirs = ['..']
            else:
                dirs = []
            dirs.extend(sorted([x.name for x in dir_ls if x.is_dir()]))
            files = sorted([x.name for x in dir_ls if x.is_file()])
            return {'dirs': dirs, 'files': files}
        else:
            raise ValueError('url is not pointing to a directory')

class Filer(JFiler):
    '''
    Same as `JFiler` when the url points to a file. If the url points to
    a directory, the content of the directory is sent as an html file
    presenting directory content as a file browser with icons instead of JSON.
    '''
    def __init__(self, root, iconer=None):
        '''
        Same as `JFiler` constructor but has an additional optional argument:
        
            * iconer: An instance of `Iconer` which will be used for the
              directories and files icons. Defaults to None which will display
              no icons.
        '''
        
        self.iconer = iconer
        self.asset_root = pathlib.Path(__file__).parent / 'asset'
        super().__init__(root)
    
    def get_content(self, handler, url, query=dict(), full_url=''):
        path = pathlib.Path(url)
        
        if self.is_dir(url) and self.is_file((path / 'index.html').as_posix()):
            url = 'index.html'
            response = http.HTTPStatus.TEMPORARY_REDIRECT
            headers = {
                    'Location': url,
                    'Content-Length': 0
                }
            f = io.BytesIO()
            return response, headers, f, lambda: None
        
        return super().get_content(handler, url, query, full_url)
    
    def serve_dir(self, handler, url, query=dict(), full_url=''):
        '''
        Overrides `JFiler.serve_dir()`. Sends an html file containing
        subdirectories and files present in the requested directory in a similar
        way to file browsers. Icons are taken from `self.iconer`.
        '''
        
        page_template = self.asset_root / 'dir_ls.html'
        with page_template.open() as f:
            page_template = f.read()
        template = self.asset_root / 'dir_ls_item.html'
        with template.open() as f:
            template = f.read()
        
        dir_ls = self.get_file_list(url, parent=bool(full_url))
        dirs = dir_ls['dirs']
        files = dir_ls['files']
        dir_ls = []
        
        full_path = pathlib.Path(full_url)
        for c in dirs:
            if c == '..':
                dir_path = '/' + full_path.parent.as_posix() + '/'
            else:
                dir_path = c + '/'
            if self.iconer is not None:
                icon_url = self.iconer.get_icon('.directory')
            else:
                icon_url = ''
            txt = template.replace('{{icon}}', icon_url)
            txt = txt.replace('{{file_name}}', c)
            txt = txt.replace('{{url}}', dir_path)
            dir_ls.append(txt)
        
        for c in files:
            if self.iconer is not None:
                icon_url = self.iconer.get_icon(c)
            else:
                icon_url = ''
            file_path = c
            txt = template.replace('{{icon}}', icon_url)
            txt = txt.replace('{{file_name}}', c)
            txt = txt.replace('{{url}}', file_path)
            dir_ls.append(txt)
        
        page = page_template.replace('{{path}}', '/' + full_url)
        page = page.replace('{{content}}', '\n'.join(dir_ls))
        f = io.BytesIO(page.encode('utf8'))
        
        response = http.HTTPStatus.OK
        length = f.seek(0, 2)
        f.seek(0)
        headers = {
                'Content-Type':'text/html',
                'Content-Length': length,
            }
        
        return response, headers, f, lambda: None

class Ziper(Filer):
    '''
    Same as `Filer` but serves the content of a zip file instead of
    a directory. The root in the constructor must be a zip file. Files served
    from this class are not seekable so resuming download is not possible for
    the content of a Ziper.
    '''
    def __init__(self, root, iconer=None):
        self.root = root
        self.iconer = iconer
        self.asset_root = pathlib.Path(__file__).parent / 'asset'
    
    def get_content(self, handler, url, query=dict(), full_url=''):
        '''
        Overrides `Filer.get_content()`. Gives the same result as
        `Filer.get_content()` but looks at the content of a zip file instead of
        a directory.
        '''
        try:
            with zipfile.ZipFile(self.root) as root:
                if self.is_dir(url) and self.is_file(url + 'index.html'):
                    url = 'index.html'
                    response = http.HTTPStatus.TEMPORARY_REDIRECT
                    headers = {
                            'Location': url,
                            'Content-Length': 0
                        }
                    f = io.BytesIO()
                    return response, headers, f, lambda: None
                
                if self.is_dir(url):
                    return self.serve_dir(handler, url, full_url=full_url, root=root)
                elif self.is_file(url):
                    return self.serve_file(handler, url, full_url=full_url, root=root)
                else:
                    return self.short_response(http.HTTPStatus.NOT_FOUND)
        except FileNotFoundError:
            logger.warning('exception in {}'.format(type(self).__name__))
            logger.warning('zip file does not exist')
            
            return self.short_response(http.HTTPStatus.NOT_FOUND)
        except Exception as e:
            logger.warning('exception in {}'.format(type(self).__name__))
            logger.warning(traceback.format_exc())
            
            return self.short_response(http.HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def serve_dir(self, handler, url, query=dict(), full_url='', root=None):
        '''
        Overrides `Filer.serve_dir()`. Looks at the content of a zip file
        instead of a directory.
        
        This method has an additional optional argument:
        
            root (`zipfile.ZipFile`): Opened `self.root` It is used in
            `self.get_content()` to avoid opening and closing `self.root`
            multiple times. Defaults to None which means `self.root` will be
            opened and a new `zipfile.ZipFile` instance will be created.
        '''
        
        page_template = self.asset_root / 'dir_ls.html'
        with page_template.open() as f:
            page_template = f.read()
        template = self.asset_root / 'dir_ls_item.html'
        with template.open() as f:
            template = f.read()
        
        full_path = pathlib.Path(full_url)
        
        dir_ls = self.get_file_list(url, root, parent=bool(full_url))
        dirs = dir_ls['dirs']
        files = dir_ls['files']
        dir_ls = []
        for c in dirs:
            if c == '..':
                dir_path = '/' + full_path.parent.as_posix() + '/'
            else:
                dir_path = c + '/'
            if self.iconer is not None:
                icon_url = self.iconer.get_icon('.directory')
            else:
                icon_url = ''
            txt = template.replace('{{icon}}', icon_url)
            txt = txt.replace('{{file_name}}', c)
            txt = txt.replace('{{url}}', dir_path)
            dir_ls.append(txt)
        
        for c in files:
            if self.iconer is not None:
                icon_url = self.iconer.get_icon(c)
            else:
                icon_url = ''
            
            file_path = c
            txt = template.replace('{{icon}}', icon_url)
            txt = txt.replace('{{file_name}}', c)
            txt = txt.replace('{{url}}', file_path)
            dir_ls.append(txt)
        
        page = page_template.replace('{{path}}', '/' + full_url)
        page = page.replace('{{content}}', '\n'.join(dir_ls))
        f = io.BytesIO(page.encode('utf8'))
        
        response = http.HTTPStatus.OK
        length = f.seek(0, 2)
        f.seek(0)
        headers = {
                'Content-Type':'text/html',
                'Content-Length': length,
            }
        
        return response, headers, f, lambda: root.close()
    
    def serve_file(self, handler, url, query=dict(), full_url='', root=None):
        '''
        Overrides `JFiler.serve_dir()`. Looks at the content of the zip file
        instead of a directory.
        
        This method has an additional optional argument:
        
            root(`zipfile.ZipFile`) Opened `self.root`. It is used in
            `self.get_content()` to avoid opening and closing `self.root`
            multiple times. Defaults to None which means `self.root` will be
            opened and a new `zipfile.ZipFile` instance will be created.
        '''
        
        if root is None:
            return self.serve_file(handler, url, query, full_url,
                    zipfile.ZipFile(self.root))
        
        zinfo = root.getinfo(url).date_time
        mtime = datetime.datetime(*zinfo)
        ifmod = handler.headers['If-Modified-Since']
        if ifmod is not None:
            ifmod = datetime.datetime.strptime(ifmod, self.HTTP_DATE_TEMPLATE)
            if mtime <= ifmod:
                response = http.HTTPStatus.NOT_MODIFIED
                headers = {}
                f = io.BytesIO(b'')
                return response, headers, f, lambda: None
        
        mime = mimetypes.guess_type(url)[0]
        f = root.open(url)
        
        response = http.HTTPStatus.OK
        length = root.getinfo(url).file_size
        headers = {
                'Content-Length':length,
                'Last-Modified': mtime.strftime(self.HTTP_DATE_TEMPLATE),
                'Cache-Control': self.MAX_AGE
            }
        
        if mime is not None:
            headers['Content-Type'] = mime
        
        return response, headers, f, lambda: root.close()
    
    def get_file_list(self, url, root=None, parent=False):
        '''
        Overrides `Filer.get_file_list()`. Looks at the content of the zip
        file instead of a directory.
        '''
        if root is None:
            with zipfile.ZipFile(self.root) as root:
                return self.get_file_list(url, root, parent=parent)
        else:
            dir_ls = [x for x in root.namelist() if x != url and x.startswith(url) and not x.split('/')[-1].startswith('.') and '/' not in x[0:-1].replace(url, '', 1)]
            if parent:
                dirs = ['..']
            else:
                dirs = []
            dirs.extend(sorted([x.split('/')[-2] for x in dir_ls if x.endswith('/')]))
            files = sorted([x.split('/')[-1] for x in dir_ls if not x.endswith('/')])
            
            return {'dirs': dirs, 'files': files}
    
    def exists(self, url, root=None):
        '''
        Overrides `Filer.exists()`. Looks at the content of the zip file
        instead of a directory.
        '''
        if not url:
            return pathlib.Path(self.root).exists()
        elif root is None:
            with zipfile.ZipFile(self.root) as root:
                return self.exists(url, root)
        else:
            try:
                path = root.getinfo(url)
                return True
            except KeyError:
                return False
    
    def is_dir(self, url, root=None):
        '''
        Overrides `Filer.is_dir()`. Looks at the content of the zip file
        instead of a directory.
        '''
        if not url:
            return pathlib.Path(self.root).exists()
        elif root is None:
            with zipfile.ZipFile(self.root) as root:
                return self.is_dir(url, root)
        else:
            try:
                path = root.getinfo(url).filename
                return not path or path.endswith('/')
            except KeyError:
                return False
        
    def is_file(self, url, root=None):
        '''
        Overrides `Filer.is_file()`. Looks at the content of the zip file
        instead of a directory.
        '''
        if root is None:
            with zipfile.ZipFile(self.root) as root:
                return self.is_file(url, root)
        else:
            try:
                path = root.getinfo(url).filename
                return not path.endswith('/')
            except KeyError:
                return False

class Iconer(Ziper):
    '''
    Same as `Ziper` but used to serve file icons used in `Filer` and `Ziper`.
    Defines methods to help other objects find icon urls for files of different
    types. The root of `Iconer` is a zip file which contains image files in its
    toplevel. The name of each image file should be in the form `<name>.<ext>`
    where `<ext>` can be any extension and <name> can be any of the following:
    
        * The string `directory`. It makes the image used as the icon for
          directories.
        * A file extension. It makes the image used for file of this extension.
        * General mimetype (such as audio, video, text, ...). It makes the image
          used for this mimetype if the file extension image does not exist.
        * The string `generic`. It makes the image used as a fallback icon if
          none of the above was found.
    
    Any file without extension in `self.root` is ignored.
    '''
    
    def __init__(self, root=None, theme='humanity', prefix='__icons__/'):
        '''
        Overrides `Ziper.__init__()`. Does not take `iconer` argument
        and always uses `self` as its `self.iconer`.
        
        args:
        
            * root (path-like object): Similar to `Ziper` constructor. If
              `None` is given the `Iconer` finds its root based on `theme`
              argument. Defaults to `None`.
            * theme (str): Ignored if `root` is not `None`. If `root` is `None`,
              looks for the root in
              `<module path>/asset/themes/<theme name>.zip` where
              `<module path>` is the path of cofan library and <theme name>
              is the value given in this argument.
            * prefix: The root url of the `Iconer` added to the `Paterner`
              class. For example, if the iconer root url is `foo_bar/`, the
              string `foo_bar` must be given in this argument and also added
              to the `Patterner` object that will relay requests to this
              `Iconer`. Defaults to `__icons__/`.
        '''
        if root is None:
            root = str(pathlib.Path(__file__).parent / 'asset' / 'themes' / '{}.zip'.format(theme))
        
        super().__init__(root, iconer=self)
        self.icon_index = self.get_icons()
        self.prefix = prefix
    
    def get_content(self, handler, url, query=dict(), full_url=''):
        if url in self.icon_index:
            url = self.icon_index[url]
            response = http.HTTPStatus.TEMPORARY_REDIRECT
            headers = {
                    'Location': url,
                    'Content-Length': 0
                }
            f = io.BytesIO()
            return response, headers, f, lambda: None
        else:
            return super().get_content(handler, url, query, full_url)
    
    def get_icons(self):
        '''
        Used in `self.__init__()`. Looks at the toplevel content of `self.root`
        for any files and makes a dictionary for each file. The keys of the
        dictionary are file names without extensions and the values are the file
        names with extensions. Any files without extension are ignored. The
        dictionary is used to look for icons without opening the zip file.
        '''
        icon_index = {}
        dir_ls = self.get_file_list('')
        for c in dir_ls['files']:
            name_ext = c.rsplit('.', 1)
            if len(name_ext) > 1:
                icon_index[name_ext[0]] = c
        
        return icon_index
    
    def get_icon(self, name):
        '''
        This method is to be used in other content providers to get icons.
        Returns the url of an icon for `name`. The icon is constructed in the
        following way:
        
            * The extension is extracted from `name`. If `name` has no
              extension, the full value of `name` is taken.
            * If there is a file in `self.root` named as the extension of `name`
              extracted in the previous step, the url of this file is
              returned. For example, if `name` is `foo.mp4`, this method will
              look for a file named `mp4.<extension>` where `<extension>` may
              be any string. The extension is case insensitive so `foo.mp4`
              will be the same as `foo.MP4`.
            * If there is no file found in the previous step, the mimetype is
              guessed and the general type is taken (such as audio,
              video, etc...).
            * If there is a file in `self.root` with the same name as the
              generel mimetype extracted in the previous step, the url of this
              file is returned. For example, if `name` is `foo.mp4`, this
              method will look for a file named `mp4.<anything>` first. If it
              there is no such file in `self.root`, the method will look for
              `video.<anything>`. `<anything>` may be any string.
            * If there is no file found in the previous step, this method looks
              for a file named `generic.<anything>` and the url of this file
              is returned.
            * If there is no file found in the previous step, an empty string
              is returned.
        '''
        ext = name.rsplit('.', 1)[-1].casefold()
        mime = mimetypes.guess_type(name)[0]
        if mime is not None:
            mime = mime.split('/')[0]
        if ext in self.icon_index:
            return (pathlib.Path(
                '/' + self.prefix) / self.icon_index[ext]).as_posix()
        elif mime is not None and mime in self.icon_index:
            return (pathlib.Path(
                '/' + self.prefix) / self.icon_index[mime]).as_posix()
        elif 'generic' in self.icon_index:
            return (pathlib.Path(
                '/' + self.prefix) / self.icon_index['generic']).as_posix()
        else:
            return ''

class PatternLister(Iconer):
    '''
    Similar to `Filer` but instead of showing content of a directory, shows the
    prefixes added to a `Patterner`. It also provides icon urls for the
    prefixes. See `Patterner` for more details of the `Patterner` provider.
    '''
    def __init__(self, provider, root=None, exclude='|__.*__/?', include='.*'):
        '''
        args:
        
            provider: The `Patterner` to list its prefixes.
            root: Same as in `Iconer`. Defaults to `None`.
            exclude: A regex `str` which will be matched to each prefix in
            `self.provider`. If the prefix matches, it will not be listed.
            Defaults to `|__.*__/?` (empty prefix or any prefix that starts and
            ends with 2 underscores).
            include: A regex `str` which will be matched to each prefix in
            `self.provider`. If the prefix does not matches, it will not be
            listed. Defaults to `.*` (any prefix).
            
        In order for a prefix to be listed and sent to the client, it must not
        match `exclude` and must match `include`. If any of them fails, the
        prefix is ignored.
        '''
        root = str(pathlib.Path(root).resolve())
        Ziper.__init__(self, root)
        self.provider = provider
        self.icon_index = self.get_icons()
        self.exclude = re.compile(exclude)
        self.include = re.compile(include)
    
    def get_content(self, handler, url, query=dict(), full_url=''):
        '''
        Overrides `Iconer.get_content()`. If the url is empty string, returns a
        list of prefixes in `self.provider`. If the url starts with
        `__pattern_icons__/`, returns an icon from `self.root`.
        '''
        if not url:
            return self.serve_patterns(handler, url, full_url=full_url)
        elif url.startswith('__pattern_icons__/'):
            url = url.replace('__pattern_icons__/', '', 1)
            return super().get_content(handler, url, query, full_url)
        else:
            return self.short_response(http.HTTPStatus.NOT_FOUND)
    
    def serve_patterns(self, handler, url, query=dict(), full_url=''):
        '''
        Same as `Filer.serve_dir()` but returns prefixes from `self.provider`
        instead of directories. Used in `self.get_content()`.
        '''
        page_template = self.asset_root / 'dir_ls.html'
        with page_template.open() as f:
            page_template = f.read()
        template = self.asset_root / 'dir_ls_item.html'
        with template.open() as f:
            template = f.read()
        
        base_url = pathlib.Path(full_url)
        if full_url:
            patterns = ['..']
        else:
            patterns = []
        patterns.extend(self.provider.get_patterns())
        content = []
        for c in patterns:
            if not self.include.fullmatch(c) or self.exclude.fullmatch(c):
                continue
            
            title = self.provider.get_title(c)
            if title:
                name = str(title)
            else:
                name = c.rstrip('/')
            icon_url = '/' + self.get_icon(c, full_url)
            pattern_url = '/' + (base_url / c).as_posix() + '/'
            txt = template.replace('{{icon}}', icon_url)
            txt = txt.replace('{{file_name}}', name)
            txt = txt.replace('{{url}}', pattern_url)
            content.append(txt)
        
        page = page_template.replace('{{path}}', '/' + full_url)
        page = page.replace('{{content}}', '\n'.join(content))
        f = io.BytesIO(page.encode('utf8'))
        
        response = http.HTTPStatus.OK
        length = f.seek(0, 2)
        f.seek(0)
        headers = {
                'Content-Type':'text/html',
                'Content-Length': length,
            }
        
        return response, headers, f, lambda: None
    def get_icon(self, name, full_url=''):
        '''
        Returns the icon of the prefix `name`. Unlike `Iconer`, this method
        takes `name` itself after striping any trailing slashes as the name of
        the icon.
        '''
        name = name.rstrip('/')
        if name in self.icon_index:
            return (pathlib.Path(full_url) / '__pattern_icons__/' / self.icon_index[name]).as_posix()
        else:
            return ''

class BaseHandler(http.server.BaseHTTPRequestHandler):
    '''
    Base http handler class in cofan library. It holds a provider instance and
    gets the response of all requests from it. Note that unlike what is usually
    done in http.server, when creating an http.HTTPServer instance, you should
    pass an instance of `BaseHandler` instead of the class itself. For example::
        
        myprovider = Filer('/path/to/my/directory')
        myhandler = BaseHandler(myprovider)
        srv = http.server.HTTPServer(('localhost', 80), myhandler)
        
    `BaseHandler` has one class attribute:
    
        __header_modifiers__: A tuple of request headers which have modifier
        methods in this class. For each header present in a request,
        `self.mod_<header>()` is called where <header> is the header name. The
        modifier method must return the response, headers and content after any
        necessary modification. It must take the following arguments:
        
            * response: Last response status code after any previous
              modifications by other modifier mehtods.
            * headers: Last headers after any previous modifications by other
              modifier mehtods.
            * content: Last content file after any previous modifications by
              other modifier mehtods.
        
        This tuple currently has only one header: `Range`. See
        `self.mod_Range()` for the modification applied.
    '''
    
    __header_modifiers__ = ('Range',)
    def __init__(self, provider):
        '''
        args:
        
            provider: The provider to get content from.
        '''
        
        self.provider = provider
    
    def do_GET(self):
        '''
        Calls `BaseProvider.get_content()` from `self.provider` and sends the
        returned response, headers and content. After this process is done,
        the content file is closed and the returned post processing fucntion is
        called. This happens regardless of whether the process ended with
        success or not.
        '''
        
        response, headers, content, postproc = self.get_response()
        try:
            self.send_response(response)
            for c in headers:
                self.send_header(c, headers[c])
            self.end_headers()
            data = content.read(1024)
            while data:
                self.wfile.write(data)
                data = content.read(1024)
        finally:
            content.close()
            postproc()
    
    def do_HEAD(self):
        '''
        Same as `self.do_GET()` but does not send any content.
        '''
        
        response, headers, content, postproc = self.get_response()
        try:
            self.send_response(response)
            for c in headers:
                self.send_header(c, headers[c])
            self.end_headers()
        finally:
            content.close()
            postproc()
    
    def get_response(self):
        '''
        Called by `self.do_GET()` and `self.do_HEAD()`. Parses the url  path and
        query string and replaces all url escapes. After that, it gets the
        response `self.provider.get_content()`. Before returning the response,
        headers, content file and post processing callables, it calls any
        modifier method that should be called. If the method fails while
        applying modifications, it closes the content file and calls the post
        processing callable before propagating the exception.
        '''
        
        url = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(url.path)[1:]
        query = urllib.parse.parse_qs(url.query)
        response, headers, content, postproc = self.provider.get_content(self, path, query, full_url=path)
        
        try:
            response_group = int(str(response.value)[0])
            if response_group != 3 and response_group != 4 and response_group != 5:
                for c in self.__header_modifiers__:
                    if c in self.headers:
                        response, headers, content = getattr(self, 'mod_{}'.format(c))(response, headers, content)
            return response, headers, content, postproc
        except:
            content.close()
            postproc()
            raise
    
    def mod_Range(self, response, headers, content):
        '''
        Called when the `Range` header is present in the request. If the
        response status code is 200 (OK) and the content file is seekable, the
        status code is changed to 206 (Partial Content) and the content file is
        changed to a partial file pointing to the requested range.
        Response status code is changed to 416 (Requested Range Not Satisfiable)
        if the range start is not between 0 and total size or if the range end
        is not between start and total size.
        '''
        
        if (response == http.HTTPStatus.OK and content.seekable() and
                Slicer is not None):
            rng = self.headers['Range'].split('=')
            if rng[0] == 'bytes':
                rng = rng[1].split('-')
                if rng[0]:
                    start = int(rng[0])
                    if rng[1]:
                        end = int(rng[1])
                    else:
                        end = content.seek(0, 2) - 1
                else:
                    start = content.seek(0, 2) - int(rng[1])
                    end = content.seek(0, 2) - 1
            else:
                raise RuntimeError('invalid range')
            
            total_size = content.seek(0, 2)
            length = end - start + 1
            
            valid_start = 0 <= start < total_size
            valid_end = start <= end < total_size
            
            if valid_start and valid_end:
                rng = 'bytes {}-{}/{}'.format(start, end, total_size)
                
                headers['Content-Range'] = rng
                headers['Content-Length'] = length
                
                response = http.HTTPStatus.PARTIAL_CONTENT
            else:
                rng = 'bytes */{}'.format(total_size)
                
                headers['Content-Range'] = rng
                headers['Content-Length'] = length
                
                response = http.HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE
            
            content = Slicer(content)(start, length)
        
        return response, headers, content
    
    def __call__(self, *args, **kwargs):
        '''
        Creates and returns another instance of the same type as `self` with
        the same provider. Any arguments and keyword arguments are passed to the
        constructor of the base class of `self`.
        '''
        
        handler = type(self)(self.provider)
        super(type(handler), handler).__init__(*args, **kwargs)
        return handler

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    '''
    same as `http.server.HTTPServer` but handles requests in daemon threads.
    '''
    
    daemon_threads = True

