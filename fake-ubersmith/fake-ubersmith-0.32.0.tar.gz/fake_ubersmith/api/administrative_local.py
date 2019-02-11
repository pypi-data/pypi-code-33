# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import request

from fake_ubersmith.api.base import Base
from fake_ubersmith.api.utils.response import response


class AdministrativeLocal(Base):
    def __init__(self):
        super().__init__()

    def hook_to(self, server):
        self.app = server
        self.app.add_url_rule('/status', view_func=self.status)
        self.app.add_url_rule('/__shutdown', view_func=self.shutdown)

    @staticmethod
    def status():
        return response(data="Service is running")

    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        self.logger.info("Shutting down server")
        return response(data="Shutting down server...")
