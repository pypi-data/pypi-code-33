# ********************************************************************************
# *   LedgerPy
# *   (c) 2019 ZondaX GmbH
# *
# *  Licensed under the Apache License, Version 2.0 (the "License");
# *  you may not use this file except in compliance with the License.
# *  You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# *  Unless required by applicable law or agreed to in writing, software
# *  distributed under the License is distributed on an "AS IS" BASIS,
# *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# *  See the License for the specific language governing permissions and
# *  limitations under the License.
# ********************************************************************************/

from ledgerblue import comm
from ledgerblue.commException import CommException


class LedgerBase:
    DEBUGMODE = False
    INS_VERSION = 0x00

    def __init__(self, cla):
        self.cla = cla
        self.last_error = None
        self._connected = False
        self._test_mode = False
        self._version_major = None
        self._version_minor = None
        self._version_patch = None

    @property
    def connected(self):
        return self._connected

    @property
    def version(self):
        return f"{self._version_major}.{self._version_minor}.{self._version_patch}"

    def send(self, ins, p1=0, p2=0, params=None):
        answer = None
        params = bytearray([]) if params is None else params

        d = None
        try:
            d = comm.getDongle(debug=self.DEBUGMODE)
            complete_message = bytearray([self.cla, ins, p1, p2, len(params)]) + params
            answer = d.exchange(complete_message)
        except CommException as e:
            print(str(type(e)), e)
            self.last_error = e.sw
        except Exception as e:
            print(str(type(e)), e)
        except BaseException as e:
            print(str(type(e)), e)
        finally:
            if d:
                d.close()

        return answer

    def connect(self):
        answer = self.send(self.INS_VERSION)
        if not answer:
            return False

        self._test_mode = (answer[0] != 0)
        self._version_major = answer[1]
        self._version_minor = answer[2]
        self._version_patch = answer[3]

        self._connected = True


def test_get_version():
    ledger = LedgerBase(0x55)
    ledger.connect()
    assert ledger.connected
