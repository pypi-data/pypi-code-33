# ----------------------------------------------------------------------------
#    Copyright 2018 MonaLabs.io
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ----------------------------------------------------------------------------
"""
A module for handling multithreading with mona contexts.

To be used only if you wish to use the same mona context in the child thread as
in the parent thread.
"""

from threading import Thread
from . import client

# TODO(itai): Add support for asyncio and greentlets if users require those.


class MonaThread(Thread):
    """
    A thread which takes care of using the same mona context as its parent
    thread.
    """

    def __init__(self, group=None, target=None, *args, **kwargs):
        self._full_context_id = ""

        def new_target(*args, **kwargs):
            with client.new_mona_context(context_id=self._full_context_id):
                target(*args, **kwargs)

        super().__init__(group=group, target=new_target, *args, **kwargs)

    def start(self):
        self._full_context_id = client.get_full_context_id()
        super().start()
