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

import os
import json

CHUNK_SIZE = 64 * 1024 * 1024
""" The default size of the chunk of the chunk
that is going to be used for file upload """

class FileAPI(object):

    @classmethod
    def _reader_g(cls, file, amount, size = 40960):
        yield amount
        while amount > 0:
            target = min(amount, size)
            chunk = file.read(target)
            yield chunk
            amount -= len(chunk)

    def session_start_file(self):
        url = self.content_url + "files/upload_session/start"
        contents = self.post(url, headers = {
            "Content-Type" : "application/octet-stream"
        })
        return contents

    def session_finish_file(
        self,
        session_id,
        data = b"",
        offset = 0,
        path = "/file",
        mode = "add",
        autorename = True,
        mute = False
    ):
        url = self.content_url + "files/upload_session/finish"
        params = dict(
            cursor = dict(
                session_id = session_id,
                offset = offset,
            ),
            commit = dict(
                path = path,
                mode = mode,
                autorename = autorename,
                mute = mute
            )
        )
        contents = self.post(
            url,
            data = data,
            headers = {
                "Content-Type" : "application/octet-stream",
                "Dropbox-API-Arg" : json.dumps(params)
            }
        )
        return contents

    def session_append_file_v2(
        self,
        session_id,
        data,
        offset = 0,
        close = False,
        timeout = 600
    ):
        url = self.content_url + "files/upload_session/append_v2"
        params = dict(
            cursor = dict(
                session_id = session_id,
                offset = offset,
            ),
            close = close
        )
        contents = self.post(
            url,
            data = data,
            headers = {
                "Content-Type" : "application/octet-stream",
                "Dropbox-API-Arg" : json.dumps(params)
            },
            timeout = timeout
        )
        return contents

    def list_folder_file(
        self,
        path,
        recursive = False,
        include_media_info = False,
        include_deleted = False,
        include_has_explicit_shared_members = False,
        limit = None,
        follow = True
    ):
        url = self.base_url + "files/list_folder"
        data_j = dict(
            path = path,
            recursive = recursive,
            include_media_info = include_media_info,
            include_deleted = include_deleted,
            include_has_explicit_shared_members = include_has_explicit_shared_members
        )
        if limit: data_j["limit"] = limit
        contents = self.post(url, data_j = data_j)
        contents_c = contents
        while True:
            has_more = contents_c.get("has_more", False)
            cursor = contents_c.get("cursor", None)
            if not follow: break
            if not has_more: break
            url = self.base_url + "files/list_folder/continue"
            contents_c = self.post(url, data_j = dict(cursor = cursor))
            contents["entries"] += contents_c.get("entries", [])
        return contents

    def upload_large_file(self, path, target, chunk_size = CHUNK_SIZE):
        cls = self.__class__
        offset = 0
        contents = self.session_start_file()
        session_id = contents["session_id"]
        file_size = os.path.getsize(path)
        file = open(path, "rb")
        try:
            while True:
                if offset == file_size: break
                amount = min(chunk_size, file_size - offset)
                self.session_append_file_v2(
                    session_id,
                    data = cls._reader_g(file, amount),
                    offset = offset
                )
                offset += amount
        finally:
            file.close()
        contents = self.session_finish_file(
            session_id,
            offset = offset,
            path = target
        )
        return contents
