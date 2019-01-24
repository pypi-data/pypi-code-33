#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Dropbox API
# Copyright (c) 2008-2018 Hive Solutions Lda.
#
# This file is part of Hive Dropbox API.
#
# Hive Dropbox API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Dropbox API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Dropbox API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import file
from . import user
from . import shared_link

BASE_URL = "https://api.dropboxapi.com/2/"
""" The default base URL to be used when no other
base URL value is provided to the constructor """

CONTENT_URL = "https://content.dropboxapi.com/2/"
""" The default content url to be used when no other
base URL value is provided to the constructor """

ACCESS_TOKEN = None
""" The default access token to be applied to the
client when no other is provided """

class API(
    appier.OAuth2API,
    file.FileAPI,
    user.UserAPI,
    shared_link.SharedLinkAPI
):

    def __init__(self, *args, **kwargs):
        appier.OAuth2API.__init__(self, *args, **kwargs)
        self.access_token = appier.conf("DROPBOX_TOKEN", ACCESS_TOKEN)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.content_url = kwargs.get("content_url", CONTENT_URL)
        self.access_token = kwargs.get("access_token", self.access_token)

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        appier.OAuth2API.build(
            self,
            method,
            url,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            params = params,
            mime = mime,
            kwargs = kwargs
        )
        if not self.is_oauth(): return
        kwargs.pop("access_token", True)
