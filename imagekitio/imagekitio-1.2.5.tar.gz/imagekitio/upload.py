''' This module contains upload apis calls '''

from __future__ import absolute_import

import time
from imagekitio import utils
import requests


class Upload(object):
    ''' Upload class '''
    def __init__(self, image=None, options=None, globl=None):
        self.image = image
        self.files = {'file': ''}
        self.option = options

        if utils.PY3:
            self.options = dict(get_defaults(), **globl)
            self.options = dict(self.options, **self.option)
        else:
            self.options = dict(get_defaults().items() + globl.items() + self.option.items())

        self.options["timestamp"] = int(time.time())

        if not verify(self.options) or not self.image:
            raise utils.Error("Invalid or missing upload parameters - %d - %s" % (2400, "BAD_REQUEST"))

        self.signature = utils.calculate_signature(self.options)


    def uploader(self):
        ''' Image upload submit function '''
        url = utils.get_protocol(False) + '//' + utils.get_image_upload_api(self.options["imagekit_id"])
        
        form_data = {
            'image': self.image,
            'filename': self.options['filename'],
            'useUniqueFilename': self.options['useUniqueFilename'],
            'folder': self.options["folder"],
            'timestamp': self.options["timestamp"],
            'apiKey': self.options["api_key"],
            'signature': self.signature
        }

        result = requests.post(url, data=form_data, files=self.files)
        return result


    def uploader_url(self):
        '''' Image upload via url submit function '''
        url = utils.get_protocol(False) + '//' + utils.get_image_upload_url_api(self.options["imagekit_id"])    
        form_data = {
            'url': self.image,
            'filename': self.options['filename'],
            'useUniqueFilename': self.options['useUniqueFilename'],
            'folder': self.options["folder"],
            'timestamp': self.options["timestamp"],
            'apiKey': self.options["api_key"],
            'signature': self.signature
        }
        result = requests.post(url, data=form_data)
        return result


def get_defaults():
    ''' return default option values '''
    return {"useUniqueFilename": True,
            "folder": "/"}


def verify(globl):
    ''' Verify global options '''
    if globl['imagekit_id'] and globl['api_key'] and globl['api_secret'] and globl['filename'] and globl['timestamp']:
        return True
    else:
        return False
