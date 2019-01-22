''' Module for initializing imagekit client '''

from __future__ import absolute_import

from imagekitio.image import Image
from imagekitio.upload import Upload
from imagekitio.admin import Admin
from imagekitio import utils


class Imagekit(object):
    ''' Imagekit client initializing class '''
    def __init__(self, args=None):
        if args:
            if utils.PY3:
                self.globl = dict(get_defaults(), **args)
            else:
                self.globl = dict(get_defaults().items() + args.items())
        else:
            self.globl = get_defaults()

        if not verify(self.globl):
            # ImageKit Id, API Key and API secret are necessary for initialization.
            raise utils.Error("ImageKit Id, API Key and API secret are necessary for initialization. - %d - %s" % (2400, "BAD_REQUEST"))


    def __str__(self):
        ''' '''
        return str(self.__class__) + ": " + str(self.__dict__)


    def image(self, key, options, signed_url=None, expiry_seconds=None):
        ''' For generating image URLs for fetching the image '''
        img = Image(key, options, self.globl)
        if signed_url:
            resp = img.signed_url(expiry_seconds)
        else:
            resp = img.url()

        return resp


    def upload(self, image, options):
        ''' For uploading the images to your imagekit account '''
        try:
            if not options['filename'] or options['filename'] == "":
                raise utils.Error("Invalid or missing upload parameters - %d - %s" % (2400, "BAD_REQUEST"))
        except:
            raise utils.Error("Invalid or missing upload parameters - %d - %s" % (2400, "BAD_REQUEST"))

        upld = Upload(image, options, self.globl)
        resp = upld.uploader()

        return resp.json()


    def upload_via_url(self, url, options):
        ''' For uploading the images via url to your imagekit account '''
        try:
            if not options['filename'] or options['filename'] == "":
                raise utils.Error("Invalid or missing upload parameters - %d - %s" % (2400, "BAD_REQUEST"))
        except:
            raise utils.Error("Invalid or missing upload parameters - %d - %s" % (2400, "BAD_REQUEST"))

        upld = Upload(url, options, self.globl)
        resp = upld.uploader_url()

        return resp.json()


    def delete_file(self, path):
        ''' For deleting the images from your imagekit's media library '''
        admin = Admin(path, self.globl)
        resp = admin.delete_file()

        return resp.json()


    def purge_file(self, url):
        ''' For purging a particular image '''
        admin = Admin(url, self.globl)
        resp = admin.purge_file()

        return resp.json()


    def list_media_files(self, skip=None, limit=None):
        ''' For purging a particular image '''
        admin = Admin('path', self.globl)
        resp = admin.list_media_files(skip, limit)

        return resp.json()


def get_defaults():
    ''' Return default values '''
    return {
        "imagekit_id": "",
        "api_key": "",
        "api_secret": "",
        "use_subdomain": None,
        "use_secure": None
    }


def verify(globl):
    ''' Verify global options '''
    if globl['imagekit_id'] and globl['api_key'] and globl['api_secret']:
        return True
    else:
        return False
