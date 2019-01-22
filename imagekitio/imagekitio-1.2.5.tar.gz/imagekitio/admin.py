''' This module have delete and purge file functions '''

from __future__ import absolute_import

import time
from imagekitio import utils
import requests


class Admin(object):
    ''' Admin class '''
    def __init__(self, path=None, globl=None):
        self.path = path
        self.files = {'image': ''}
        # print(globl.items())

        self.options = dict({'path' : path}, **globl)

        self.options["timestamp"] = int(time.time())

        if not self.path:
            raise utils.Error("Invalid or missing upload parameters - %d - %s" % (1400, "BAD_REQUEST"))


    def delete_file(self):
        ''' Delete file post request '''

        url = utils.get_protocol(False) + '//' + utils.get_image_delete_api()
        signature = utils.calculate_delete_signature(self.options)

        form_data = {
            'path': self.options['path'],
            'imagekitId': self.options['imagekit_id'],
            'signature': signature
        }
        result = requests.post(url, data=form_data)
        return result


    def purge_file(self):
        ''' Purge file post request '''

        url = utils.get_protocol(False) + '//' + utils.get_image_purge_api()
        signature = utils.calculate_purge_signature(self.options)
        form_data = {
            'url': self.options['path'],
            'imagekitId': self.options['imagekit_id'],
            'signature': signature
        }

        result = requests.post(url, data=form_data)
        return result


    def list_media_files(self, skip=0, limit=1000):
        ''' list files post request '''

        self.options = dict({'skip': str(skip), 'limit': str(limit)}, **self.options)

        url = utils.get_protocol(False) + '//' + utils.get_list_media_api()
        signature = utils.calculate_list_media_signature(self.options)

        url =  url + '?skip=' + self.options['skip'] + '&limit=' + self.options['limit'] + '&imagekitId=' + self.options['imagekit_id'] + '&signature=' + signature

        result = requests.get(url)
        return result
