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

import logging

from flask.app import Flask

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.administrative_local import AdministrativeLocal
from fake_ubersmith.api.methods.client import Client
from fake_ubersmith.api.methods.order import Order
from fake_ubersmith.api.methods.uber import Uber
from fake_ubersmith.api.methods.vendor_modules.iweb import IWeb
from fake_ubersmith.api.ubersmith import UbersmithBase


def _get_logger(logging_app):
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s', "%Y-%m-%d %H:%M:%S")
    )
    logging_app.logger.addHandler(handler)
    logging_app.logger.setLevel(logging.INFO)


def run():
    # TODO (wajdi) Make configurable passed parameter
    port = 9131

    app = Flask('fake_ubersmith')

    data_store = DataStore()
    base_uber_api = UbersmithBase(data_store)

    AdministrativeLocal().hook_to(app)

    Uber(data_store).hook_to(base_uber_api)
    Order(data_store).hook_to(base_uber_api)
    Client(data_store).hook_to(base_uber_api)
    IWeb(data_store).hook_to(base_uber_api)

    base_uber_api.hook_to(app)

    _get_logger(app)

    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    run()
