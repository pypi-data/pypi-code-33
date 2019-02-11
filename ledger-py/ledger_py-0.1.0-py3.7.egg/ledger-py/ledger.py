from __future__ import print_function

import binascii
import time

from ledgerblue import commU2F, comm
from ledgerblue.commException import CommException

CLA = 0x77

INS_VERSION = 0x00
INS_GETSTATE = 0x01
INS_PUBLIC_KEY = 0x03
INS_SIGN = 0x04
INS_SIGN_NEXT = 0x05
INS_TEST_PK_GEN_1 = 0x80
INS_TEST_PK_GEN_2 = 0x81
INS_TEST_CALC_PK = 0x82
INS_TEST_WRITE_LEAF = 0x83
INS_TEST_READ_LEAF = 0x84
INS_TEST_KEYGEN = 0x85
INS_TEST_DIGEST = 0x86
INS_TEST_SETSTATE = 0x87
INS_TEST_COMM = 0x88

last_error = 0

APPMODE_NOT_INITIALIZED = 0x00
APPMODE_KEYGEN_RUNNING = 0x01
APPMODE_READY = 0x02

VERSION_MIN_MAJOR = 0
VERSION_MIN_MINOR = 2
VERSION_MIN_PATCH = 0


class LedgerQRL(object):
    SCRAMBLE_KEY = "QRL"
    U2FMODE = True
    DEBUGMODE = False

    def __init__(self):
        self.last_error = None
        self._connected = False

        self._test_mode = False
        self._version_major = None
        self._version_minor = None
        self._version_patch = None

        self._mode_str = 'unknown'
        self._mode_code = -1

        self._pk_raw = None
        self._otsindex = None

    @property
    def connected(self):
        return self._connected

    @property
    def test_mode(self):
        return self._test_mode

    @property
    def version(self):
        return "{}.{}.{}".format(self._version_major, self._version_minor, self._version_patch)

    @property
    def mode(self):
        return self._mode_str

    @property
    def mode_code(self):
        return self._mode_code

    @property
    def pk(self):
        if self._pk_raw is None:
            return None

        return binascii.hexlify(self._pk_raw).decode()

    @property
    def pk_raw(self):
        return self._pk_raw

    def print_info(self):
        if self._test_mode:
            print("WARNING! TEST MODE ENABLED")
        print("Version    : {}".format(self.version))
        print("Mode       : {}".format(self.mode))

        print("XMSS Index : {}".format(self._otsindex))

        if self.pk:
            print("Public Key : {}".format(self.pk))

    def connect(self):
        self.U2FMODE = False

        # Check version
        answer = self.send(INS_VERSION)
        if answer is None:
            return False

        self._test_mode = (answer[0] != 0)
        self._version_major = answer[1]
        self._version_minor = answer[2]
        self._version_patch = answer[3]

        answer = self.send(INS_GETSTATE)
        if answer is None:
            return False

        self._mode_code = answer[0]
        self._mode_str = "Unknown"

        self._otsindex = 1 + answer[1] + answer[2] * 256

        if answer[0] == APPMODE_NOT_INITIALIZED:
            self._mode_str = "not initialized"

        if answer[0] == APPMODE_KEYGEN_RUNNING:
            self._mode_str = "keygen running"

        if answer[0] == APPMODE_READY:
            self._mode_str = "ready"
            answer = self.send(INS_PUBLIC_KEY)
            self._pk_raw = answer

        self._connected = True

    def sign(self, message):
        if not self.connected:
            raise Exception("Device is not connected or reacheable")

        print("Signing...")
        answer = self.send(INS_SIGN, 0, 0, message)
        if answer is None:
            raise Exception("Sign Operation Rejected")

        signature = b''
        for i in range(11):
            answer = self.send(INS_SIGN_NEXT)
            answer = binascii.hexlify(answer).upper()
            signature += answer
            if self.DEBUGMODE:
                print("[{}] {}".format(len(answer) / 2, answer))

        if self.DEBUGMODE:
            print("[{}] {}".format(len(signature) / 2, signature))

        return binascii.unhexlify(signature)

    def send(self, ins, p1=0, p2=0, params=None):
        answer = None
        if params is None:
            params = bytearray([])

        start = time.time()
        dongle = None
        try:
            if self.U2FMODE:
                dongle = commU2F.getDongle(scrambleKey=self.SCRAMBLE_KEY, debug=self.DEBUGMODE)
            else:
                dongle = comm.getDongle(debug=self.DEBUGMODE)

            cmd = bytearray([CLA, ins, p1, p2, len(params)]) + params
            answer = dongle.exchange(cmd)
        except CommException as e:
            print("LEDGERQRL: COMMEXC: ", e)
            self.last_error = e.sw
        except Exception as e:
            print("LEDGERQRL: Exception: ", e)
        except BaseException as e:
            print("LEDGERQRL: BaseException: ", e)
        finally:
            if dongle is not None:
                dongle.close()

        if self.U2FMODE:
            if answer is not None:
                if self.DEBUGMODE:
                    print("U2F[{}]: {}".format(len(answer), binascii.hexlify(answer)))
                answer = answer[5:]

        end = time.time()
        if self.DEBUGMODE:
            print(end - start)
        return answer
