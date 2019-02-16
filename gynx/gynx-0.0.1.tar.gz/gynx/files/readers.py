# -*- coding: UTF-8 -*-
from stat import ST_SIZE, ST_MTIME
import mimetypes
import sys
import os
import time
import json

class FileReader(object):

    def __init__(self, src, *args, **kwargs):
        #self.saved = self.open_json()
        self.quiet = False
        self.initial = False
        self.src = src

    @property
    def cache(self):
        return self.src + 'CACHE/' + self.filename

    @property
    def files(self):
        files = self.get()
        if not self.load():
            self.initial = True
        self.save(files)
        return files

    @property
    def json(self):
        return json.dumps(self.files, default=lambda o: time.asctime(o), indent=4, sort_keys=True)

    def save(self, files):
        with open(self.cache, 'w') as jsonfile:
            json.dump(files, jsonfile, default=lambda o: time.asctime(o), indent=4, sort_keys=True)

    def load(self):
        try:
            with open(self.cache, 'r') as jsonfile:
                return json.load(jsonfile)
        except IOError:
            return None

    def size(self, item):
        '''
        Return file size if present. If not, return 0.
        '''
        return int(item['size']) if 'size' in item.keys() else 0

    def completion(self, items, usage):
        '''
        Animated progress bar printed to sys.stdout
        '''
        size = float(sum([self.size(item) for item in items]))
        if int(usage) == 0:
            empty = True
            usage = float(1)
        else:
            empty = False
        completion = (size / usage) * 100
        percent = 100 if completion >= 100 else int(completion)
        if empty:
            percent = 100
        filled = int(percent / 4)
        done = '=' * filled
        remaining = ' ' * (25 - filled)
        sys.stdout.write('\r|%s%s| %d%% - %d files' % (done, remaining, percent, len(items)))
        sys.stdout.flush()
        return completion

class RemoteFileReader(FileReader):

    def __init__(self, src, service, info, *args, **kwargs):
        super(RemoteFileReader, self).__init__(src, service, info, *args, **kwargs)
        self.service = service
        self.filename = 'remote.json'
        self.info = info
        self.remote_folders = {}

    def get(self):
        return self.index_files(self.fetch())

    def fetch(self):
        '''
        Full list of remote files as JSON objects.
        '''
        fields = 'nextPageToken, files(id, name, size, modifiedTime, mimeType, parents)'
        info = self.info
        usage = float(info['storageQuota']['usageInDrive'])
        results = self.service.files().list(pageSize=1000, fields=fields).execute()
        items = results.get('files', [])
        print('Gathering remote files...')
        if not self.quiet:
            self.completion(items, usage)
        page_token = results.get('nextPageToken')
        while page_token:
            page_results = self.service.files().list(pageSize=1000, pageToken=page_token, fields=fields).execute()
            page_items = page_results.get('files', [])
            items += page_items
            if not self.quiet:
                self.completion(items, usage)
            page_token = page_results.get('nextPageToken')
        sys.stdout.write('\n')
        self.remote_files = items
        return items

    def parent(self, f):
        '''
        Return first parent in parents list.
        '''
        if 'parents' in f.keys():
            if len(f['parents']) > 0:
                return f['parents'][0]
        return None

    def get_path(self, f, files):
        '''
        Get the file path of a remote file relative to /
        '''
        path = f['name']
        while True:
            parent = self.parent(f)
            f = self.get_object(parent, files)
            if f:
                path = f['name'] + '/' + path
            else:
                return '/' + path

    def get_object(self, fid, files):
        '''
        Return a file dictionary object from the files list by querying the ID
        '''
        return next((x for x in files if x['id'] == fid), None)

    def index(self, files, directory):
        '''
        Recursively index remote subfolders into nested dictionaries
        '''
        result = {}
        for child in files:
            parent = self.get_object(self.parent(child), files)
            if parent:
                if parent['name'] == directory:
                    if 'folder' in child['mimeType']:
                        folderpath = self.get_path(child, files)
                        self.remote_folders[folderpath] = child['id']
                        result[child['name']] = self.index(files, child['name'])
                    else:
                        filepath = self.get_path(child, files)
                        result[child['name']] = {
                            #'type': 'file',
                            'path': filepath,
                            'mimetype': child['mimeType'],
                            'extension': os.path.splitext(filepath)[1][1:].upper(),
                            'size': int(child['size']),
                            'modified': time.strptime(
                                ' '.join(child['modifiedTime'][:-5].split('T')),
                                '%Y-%m-%d %H:%M:%S'
                            ),
                            'child_id': child['id'],
                            'parent_id': parent['id'],
                        }
        return result


    def index_files(self, files):
        '''
        Parse remote file list and return nested dictionary of file hierarchy
        '''
        result = {}
        for child in files:
            parent = self.get_object(self.parent(child), files)
            if not parent:
                if 'folder' in child['mimeType']:
                    folderpath = self.get_path(child, files)
                    self.remote_folders[folderpath] = child['id']
                    result[child['name']] = self.index(files, child['name'])
                else:
                    filepath = self.get_path(child, files)
                    result[child['name']] = {
                        #'type': 'file',
                        'path': filepath,
                        'mimetype': child['mimeType'],
                        'extension': os.path.splitext(filepath)[1][1:].upper(),
                        'size': int(child['size']),
                        'modified': time.strptime(
                            ' '.join(child['modifiedTime'][:-5].split('T')),
                            '%Y-%m-%d %H:%M:%S'
                        ),
                        'child_id': child['id'],
                    }
        final = {'drive': result}
        return final

class LocalFileReader(FileReader):

    def __init__(self, src, rootdir, *args, **kwargs):
        super(LocalFileReader, self).__init__(src, rootdir, *args, **kwargs)
        self.rootdir = rootdir
        self.filename = 'local.json'

    def get(self):
        '''
        Creates a nested dictionary that represents the folder structure of rootdir
        '''
        print('Indexing local directory...')
        result = {}
        rootdir = self.rootdir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            '''
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
            '''
            files_dict = {}
            for f in files:
                filepath = '%s/%s' % (path, f)
                relative_path = path[path.index(rootdir) + len(rootdir): len(path)]
                relative_filepath = '%s/%s' % (relative_path, f)
                files_dict[f] = {
                    #'type': 'file',
                    'path': relative_filepath,
                    'mimetype': mimetypes.guess_type(filepath)[0],
                    'extension': os.path.splitext(filepath)[1][1:].upper(),
                    'size': int(os.stat('%s/%s' % (path, f))[ST_SIZE]),
                    'modified': time.localtime(os.stat(filepath)[ST_MTIME])
                }
            folders = path[start:].split(os.sep)
            subdir = files_dict
            #subdir = OrderedDict(sorted(files_dict.items(), key=lambda(k, v): k.upper()))
            #subdir['__path__'] = path
            #subdir['__resource_type__'] = 'folder'
            parent = reduce(dict.get, folders[:-1], result)
            parent[folders[-1]] = subdir
        final = {'drive': result[rootdir.split('/')[-1]]}
        return final
