#!/usr/bin/python2.7

class Changes():

    def get(self):
        '''
        Full list of changes to remote file system.
        '''
        fields = 'nextPageToken, changes(time, removed)'
        ptr = self.service.changes().getStartPageToken().execute()
        page_token = ptr['startPageToken']
        changes = []
        while page_token is not None:
            response = self.service.changes().list(
                pageToken=page_token, spaces='drive', fields=fields).execute()
            for change in response.get('changes'):
                changes.append(change)
                print('Change found for file: %s' % change.get('fileId'))
            page_token = response.get('nextPageToken')
        return changes
