#!/usr/bin/env python3

import logging

endpoints = { 'get_file': 'https://beep.metid.polimi.it/api/secure/jsonws/'
             'dlapp/get-file-entries?repositoryId=%d&folderId=%d',
             'get_folders': 'https://beep.metid.polimi.it/api/secure/jsonws'
             '/dlapp/get-folders?repositoryId=%d&parentFolderId=%d',
             'get_user_sites': 'https://beep.metid.polimi.it/api/secure/'
             'jsonws/group/get-user-sites',
             'download_file': 'https://beep.metid.polimi.it/c/'
             'document_library/get_file?groupId=%d&folderId=%d&title=%s'
            }

api_logger = logging.getLogger("polibeepsync.beep_api")

class BeepSession():
    def __init__(self):
        pass

    def login(self):
        api_logger.info('Logging in.')
        

