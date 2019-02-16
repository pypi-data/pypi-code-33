#!/usr/bin/python2.7

import io, os
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError


class SyncOperations(object):

    def __init__(self, service, changes, remote=None, local=None, root=".", rf=None, *args, **kwargs):
        self.service = service
        self.changes = changes
        self.remote = remote
        self.local = local
        self.root = root
        self.current = None
        self.rf = rf

    def get_relative_path(self, path):
        return path.split(self.root)[-1]

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

    def download(self, path, file_id):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print "Download %d%%." % int(status.progress() * 100)

    def upload(self, f, local_path, folder=None):
        file_metadata = {'name': local_path.split('/')[-1]}
        if folder:
            file_metadata['parents'] = [folder]
        media = MediaFileUpload(local_path, mimetype=f['mimetype'], resumable=True)
        file = self.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        # print 'File ID: %s' % file.get('id')


    def create_folder(self, name, target, path):
        if target == 'remote':
            data = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=data, fields='id').execute()
            return folder.get('id')
        else:
            os.mkdir(path)
            return None

    def run(self):
        current = self.current
        for change in self.changes:
            #if change['type']  == 'rename':
            #    continue
            print change['message']
            if change['target'] == 'remote':
                if change['type']  == 'rename':
                    continue
                f = self.get_file_by_path(self.get_relative_path(change['local_path']), self.local)
                try:
                    if f:
                        parent_name = f['path'].split('/')[-2]
                    else:
                        parent_name = None
                except KeyError or IndexError:
                    parent_name = None
                if parent_name and f:
                    local_parent = self.get_file_by_path(
                        self.get_relative_path("/".join(f['path'].split('/')[:-1])[1:]),
                        self.local
                    )
                    remote_parent = self.get_file_by_path(
                        self.get_relative_path("/".join(f['path'].split('/')[:-1])[1:]),
                        self.remote
                    )
                    if local_parent:
                        folder_path = "/".join(f['path'].split('/')[:-1])
                        if self.rf.get(folder_path):
                            current = self.rf.get(folder_path)
                    elif remote_parent:
                        if len(remote_parent.values()) > 0:
                            current = remote_parent.values()[0].get('parent_id')
                    else:
                        current = None
                else:
                    current = None
                if f or f == {}:
                    # If file type is folder, create folder
                    if change['folder']:
                        folder = self.create_folder(
                            name=change['local_path'].split('/')[-1],
                            target='remote',
                            path=None
                        )
                        current = folder
                    else:
                        # File created in local, upload remote
                        if change['type'] == 'change':
                            # File changed in local, delete first
                            self.service.files().delete(fileId=change['remote_id']).execute()
                        if f:
                            self.upload(f, change['local_path'], folder=current)
                else:
                    # File deleted in local, delete remote
                    if change.get('remote_id'):
                        rid = change.get('remote_id')
                    else:
                        rid = self.rf.get(u'/'+change['local_path'].split(self.root)[-1])
                    try:
                        self.service.files().delete(fileId=rid).execute()
                    except HttpError:
                        print u'Remote file not found: %s' % u'/'+change['local_path'].split(self.root)[-1]
            else:
                if change['type']  == 'rename':
                    continue
                f = self.get_file_by_path(self.get_relative_path(change['local_path']), self.remote)
                if f or f == {}:
                    # If file type is folder, create folder
                    if change['folder']:
                        self.create_folder(
                            name=change['local_path'].split('/')[-1],
                            target='local',
                            path=change['local_path']
                        )
                    else:
                        # File created/updated in remote, download to local
                        self.download(change['local_path'], change['remote_id'])
                else:
                    # File deleted in remote, delete local
                    os.remove(change['local_path'])
