#!/usr/bin/python2.7
import dictdiffer
import os

class Difference(object):
    '''
    An object that represents a difference between two nested file structure
    differences. Object properties are parsed from each item in a dictdiffer
    list.
    '''

    def __init__(self, dd, *args, **kwargs):
        self.dd = dd

    def __str__(self):
        return str(self.dd)

    @property
    def type(self):
        return self.dd[0]

    @property
    def path(self):
        if self.type == 'change':
            return '/'.join(self.dd[1][1:len(self.dd[1])-1])
        elif self.type == 'add' or self.type == 'remove':
            if type(self.dd[1]) == type('s') or type(self.dd[1]) == type(u's'):
                return '/'.join(self.dd[1].split('.')[1:])
            elif type(self.dd[1]) == type(list([1, 2, 3])):
                return '/'.join(self.dd[1][1:])
            else:
                print(type(self.dd[1]))
                raise IOError("Cannot parse path %s" % str(self.dd[1]))
        else:
            raise TypeError('Invalid difference type: %s' % str(self.type))

    @property
    def key(self):
        if self.type == 'change':
            return self.dd[1][-1]
        else:
            return None

    @property
    def target(self):
        if self.type == 'add' or self.type == 'remove':
            return self.dd[2]
        else:
            return None

    @property
    def remote_modified(self):
        if self.type == 'change':
            return self.dd[2][0]
        else:
            return None

    @property
    def local_modified(self):
        if self.type == 'change':
            return self.dd[2][1]
        else:
            return None

class Differences(object):

    def __init__(self, remote_files, local_files, previous=None, initial=False, root='.'):
        self.debug = True
        self.remote = remote_files
        self.local = local_files
        self.rootdir = root
        self.first_run = initial
        if previous:
            self.previous = previous
        else:
            self.previous = remote_files

    def all(self):
        return self.merge(self.remote, self.local)

    def get(self, remote, local):
        '''
        Get the differences between two nested dictionaries (in both directions)
        '''
        return (
            [Difference(d) for d in list(dictdiffer.diff(remote, local))],
            [Difference(d) for d in list(dictdiffer.diff(local, remote))]
        )

    def get_file_by_path(self, path, files):
        '''
        Locate a file in a nested folder dictionary and return file properties.
        Return None if file not found.
        '''
        d = files['drive']
        for section in path.split('/'):
            if len(section) > 0:
                try:
                    d = d[section]
                except:
                    return None
        return d

    def get_id(self, f):
        try:
            return f['child_id']
        except:
            return None

    def print_all(self):
        for diff in self.all():
            try:
                print diff['message']
            except:
                print diff

    def merge(self, remote, local, differences=[], startpath=""):
        '''
        Merge the differences into one list of Difference objects.
        '''
        lr, rl = self.get(remote, local)
        for ld in lr:
            for rd in rl:
                if ld.path == rd.path:
                    if ld.type == 'change' and ld.key == 'modified':
                        local_file = self.get_file_by_path(ld.path, local)
                        remote_file = self.get_file_by_path(rd.path, remote)
                        if int(local_file['size']) != int(remote_file['size']):
                            diff = {}
                            f = self.get_file_by_path(ld.path, self.previous)
                            diff['type'] = 'change'
                            diff['folder'] = False
                            diff['local_path'] = self.rootdir + ld.path
                            diff['remote_id'] = self.get_id(f)
                            if ld.remote_modified < ld.local_modified:
                                diff['target'] = 'remote'
                                diff['message'] = '%s updated in local. Uploading...' % ld.path
                            else:
                                diff['target'] = 'local'
                                diff['message'] = '%s updated in remote. Downloading...' % ld.path
                            if diff not in differences and len(diff) > 0:
                                differences.append(diff)
                    elif ld.type == 'add' or ld.type == 'remove' and ld.target == rd.target:
                        for item in ld.target:
                            if item[0] != 'child_id' and item[0] != 'parent_id':
                                diff = {}
                                homepath = os.path.join(startpath, ld.path, item[0])
                                if len(startpath) == 0:
                                    try:
                                        homepath = startpath + item[1].get('path')
                                    except TypeError:
                                        homepath = homepath
                                if homepath.startswith('/'):
                                    homepath = homepath[1:]
                                diff['folder'] = False
                                f = self.get_file_by_path(homepath, self.previous)
                                remote_file = self.get_file_by_path(homepath, self.remote)
                                if remote_file or remote_file == {}:
                                    if not remote_file.get('mimetype') and not remote_file.get('path') and not remote_file.get('modified'):
                                        diff['folder'] = True
                                local_file = self.get_file_by_path(homepath, self.local)
                                if local_file or local_file == {}:
                                    if not local_file.get('mimetype') and not local_file.get('path') and not local_file.get('modified'):
                                        diff['folder'] = True
                                diff['local_path'] = self.rootdir + homepath
                                diff['remote_id'] = self.get_id(remote_file) if remote_file else None
                                if ld.type == 'add' and rd.type == 'remove':
                                    if f:
                                        diff['type'] = 'remove'
                                        diff['target'] = 'local'
                                        diff['message'] = '%s removed in remote. Deleting local...' % homepath
                                    else:
                                        diff['type'] = 'add'
                                        diff['target'] = 'remote'
                                        if diff['folder']:
                                            diff['message'] = '%s created in local. Creating remote directory...' % homepath
                                        else:
                                            diff['message'] = '%s created in local. Uploading...' % homepath
                                elif ld.type == 'remove' and rd.type == 'add':
                                    file_or_folder = f or f == {}
                                    if file_or_folder and not self.first_run:
                                        diff['type'] = 'remove'
                                        diff['target'] = 'remote'
                                        diff['message'] = '%s removed in local. Deleting remote...' % homepath
                                    else:
                                        diff['type'] = 'add'
                                        diff['target'] = 'local'
                                        if diff['folder']:
                                            diff['message'] = '%s created in remote. Creating local directory...' % homepath
                                        else:
                                            diff['message'] = '%s created in remote. Downloading...' % homepath
                                else:
                                    diff['type'] = 'rename'
                                    lname, rname = ld.dd[2][0][0], rd.dd[2][0][0]
                                    if remote_file:
                                        diff['target'] = 'local'
                                        diff['new'] = rname
                                        diff['message'] = '%s renamed in remote to %s. Renaming local...' % (lname, rname)
                                    elif local_file:
                                        diff['target'] = 'remote'
                                        diff['new'] = lname
                                        diff['message'] = '%s renamed in local to %s. Renaming remote...' % (rname, lname)
                                if diff not in differences and len(diff) > 0:
                                    differences.append(diff)
                                if diff['folder']:
                                    local_folder = self.get_file_by_path(homepath, self.local)
                                    if not local_folder:
                                        local_folder = {}
                                    remote_folder = self.get_file_by_path(homepath, self.remote)
                                    if not remote_folder:
                                        remote_folder = {}
                                    self.merge(remote_folder, local_folder, differences, startpath=homepath)
        if len(differences) == 0:
            print("No changes!")
        return differences
