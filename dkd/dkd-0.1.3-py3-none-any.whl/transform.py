# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Message Transforming
    ~~~~~~~~~~~~~~~~~~~~

    Instant Message <-> Secure Message <-> Reliable Message
    +-------------+     +------------+     +--------------+
    |  sender     |     |  sender    |     |  sender      |
    |  receiver   |     |  receiver  |     |  receiver    |
    |  time       |     |  time      |     |  time        |
    |             |     |            |     |              |
    |  content    |     |  data      |     |  data        |
    +-------------+     |  key/keys  |     |  key/keys    |
                        +------------+     |  signature   |
                                           +--------------+
    Algorithm:
        data      = password.encrypt(content)
        key       = public_key.encrypt(password)
        signature = private_key.sign(data)
"""

import json

from mkm.utils import base64_encode, base64_decode
from mkm import SymmetricKey, PublicKey, PrivateKey
from mkm import ID, Meta, Group

from dkd.content import Content
from dkd.message import Envelope, Message


def json_str(dictionary):
    """ convert a dict to json str """
    return json.dumps(dictionary)


def json_dict(string):
    """ convert a json str to dict """
    return json.loads(string)


class KeyMap(dict):
    """
        Encrypted Key Map for Secure Group Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        data format: {
            "ID1": "{key1}", // base64_encode(asymmetric)
        }
    """

    def __new__(cls, keys: dict={}):
        self = super().__new__(cls, keys)
        return self

    def __getitem__(self, identifier: ID) -> bytes:
        if identifier in self:
            item = super().__getitem__(identifier)
            return base64_decode(item)
        else:
            return None

    def __setitem__(self, identifier: ID, data: bytes):
        if data:
            item = base64_encode(data)
            super().__setitem__(identifier, item)
        elif identifier in self:
            self.pop(identifier)  # remove it


class InstantMessage(Message):
    """
        This class is used to create an instant message
        which extends 'content' field from Message
    """

    def __new__(cls, msg: dict):
        self = super().__new__(cls, msg)
        # message content
        self.content = Content(msg['content'])
        return self

    @classmethod
    def new(cls, content: Content, envelope: Envelope=None,
            sender: ID=None, receiver: ID=None, time: int=0):
        if envelope:
            sender = envelope.sender
            receiver = envelope.receiver
            time = envelope.time
        # build instant message info
        msg = {
            'sender': sender,
            'receiver': receiver,
            'time': time,

            'content': content,
        }
        return InstantMessage(msg)

    def encrypt(self, password: SymmetricKey,
                public_key: PublicKey=None, public_keys: dict=None):
        """
        Encrypt message content with password(key)

        :param password:    A symmetric key for encrypting message content
        :param public_key:  A asymmetric key for encrypting the password
        :param public_keys: PublicKeys for group message
        :return: SecureMessage object
        """
        data = json_str(self.content).encode('utf-8')
        data = password.encrypt(data)
        key = json_str(password).encode('utf-8')
        # build secure message info
        msg = self.copy()
        msg.pop('content')
        msg['data'] = base64_encode(data)
        # check receiver
        receiver = self.envelope.receiver
        if receiver.address.network.is_communicator():
            # personal message
            if public_key is None and receiver in public_keys:
                # get public key data from the map
                # and convert to a PublicKey object
                public_key = PublicKey(public_keys[receiver])
            # encrypt the symmetric key with the receiver's public key
            # and save in msg.key
            msg['key'] = base64_encode(public_key.encrypt(key))
        elif receiver.address.network.is_group() and receiver == self.content.group:
            # group message
            keys = KeyMap()
            group = Group(receiver)
            for member in group.members:
                if member in public_keys:
                    # get public key data from the map
                    # and convert to a PublicKey object
                    public_key = PublicKey(public_keys[receiver])
                    # encrypt the symmetric key with the member's public key
                    # and save in msg.keys
                    keys[member] = public_key.encrypt(key)
                else:
                    raise LookupError('Public key not found for member: ' + member)
            msg['keys'] = keys

        else:
            raise ValueError('Receiver error')
        # OK
        return SecureMessage(msg)


class SecureMessage(Message):
    """
        This class is used to encrypt/decrypt instant message
        which replace 'content' field with an encrypted 'data' field
        and contain the key (encrypted by the receiver's public key)
        for decrypting the 'data'
    """

    def __new__(cls, msg: dict):
        self = super().__new__(cls, msg)
        # secure(encrypted) data
        self.data = base64_decode(msg['data'])
        # decrypt key/keys
        if 'key' in msg:
            self.key = base64_decode(msg['key'])
            self.keys = None
        elif 'keys' in msg:
            self.key = None
            self.keys = KeyMap(msg['keys'])
        else:
            # reuse key/keys
            self.key = None
            self.keys = None
        # Group ID
        #   when a group message was split/trimmed to a single message,
        #   the 'receiver' will be changed to a member ID, and
        #   the 'group' will be set with the group ID.
        if 'group' in msg:
            group = ID(msg['group'])
            if group.address.network.is_group():
                self.group = group
            else:
                raise ValueError('Group ID error')
        else:
            self.group = None
        return self

    def decrypt(self, password: SymmetricKey=None,
                private_key: PrivateKey=None) -> InstantMessage:
        """
        Decrypt message data to plaintext content
        :param password:    Reusable password
        :param private_key: User's private key for decrypting password
        :return: InstantMessage object
        """
        receiver = self.envelope.receiver
        if receiver.address.network.is_communicator():
            if private_key:
                # get password from key/keys
                if self.key:
                    key = self.key
                elif self.keys:
                    key = self.keys[receiver]
                else:
                    key = None
                # decrypt key data with receiver's private key
                if key:
                    key = json_dict(private_key.decrypt(key))
                    password = SymmetricKey(key)
            if password:
                # decrypt data with password
                msg = self.copy()
                msg.pop('data')
                if 'key' in msg:
                    msg.pop('key')
                if 'keys' in msg:
                    msg.pop('keys')
                msg['content'] = json_dict(password.decrypt(self.data))
                return InstantMessage(msg)
            else:
                raise AssertionError('No password to decrypt message content')
        elif receiver.address.network.is_group():
            raise AssertionError('Trim group message for a member first')
        else:
            raise ValueError('Receiver type not supported')

    def sign(self, private_key: PrivateKey):
        """
        Sign the message.data

        :param private_key: User's private key
        :return: ReliableMessage object
        """
        signature = private_key.sign(self.data)
        msg = self.copy()
        msg['signature'] = base64_encode(signature)
        return ReliableMessage(msg)

    def split(self, group: Group) -> list:
        """ Split the group message to single person messages """
        receiver = self.envelope.receiver
        if receiver.address.network.is_group():
            if group.identifier != receiver:
                raise AssertionError('Group not match')
            msg = self.copy()
            msg['group'] = receiver
            if 'keys' in msg:
                msg.pop('keys')
            messages = []
            for member in group.members:
                msg['receiver'] = member
                if self.keys and member in self.keys:
                    msg['key'] = base64_encode(self.keys[member])
                elif 'key' in msg:
                    msg.pop('key')  # reused key
                messages.append(SecureMessage(msg))
            return messages
        else:
            raise AssertionError('Only group message can be split')

    def trim(self, member: ID, group: Group=None):
        """ Trim the group message for a member """
        receiver = self.envelope.receiver
        if receiver.address.network.is_communicator():
            if not member or member == receiver:
                return self
            else:
                raise AssertionError('Receiver not match')
        elif receiver.address.network.is_group():
            if group is None or group.identifier != receiver:
                raise AssertionError('Group not match')
            if member:
                # make sure it's the group's member
                if not group.hasMember(member):
                    raise AssertionError('Member not found')
            elif self.keys and len(self.keys) == 1:
                # the only key is for you, maybe
                member = self.keys.keys()[0]
            elif len(group.members) == 1:
                # you are the only member of this group
                member = group.members[0]
            else:
                raise AssertionError('Who are you?')
            # build Message info
            msg = self.copy()
            msg['group'] = receiver
            msg['receiver'] = member
            if self.keys:
                msg.pop('keys')
                if member in self.keys:
                    msg['key'] = base64_encode(self.keys[member])
            return SecureMessage(msg)
        else:
            raise AssertionError('Receiver type not supported')


class ReliableMessage(SecureMessage):
    """
        This class is used to sign the SecureMessage
        It contains a 'signature' field which signed with sender's private key
    """

    def __new__(cls, msg: dict):
        self = super().__new__(cls, msg)
        # signature
        self.signature = base64_decode(msg['signature'])
        # meta info of sender, just for the first contact with the station
        if 'meta' in msg:
            self.meta = Meta(msg['meta'])
        return self

    def verify(self, public_key: PublicKey=None) -> SecureMessage:
        if public_key is None:
            # try to get public key from meta
            if self.meta and self.meta.match_identifier(self.envelope.sender):
                public_key = self.meta.key
            else:
                raise AssertionError('Cannot get public key from message.meta')
        # verify and build a SecureMessage object
        if public_key.verify(self.data, self.signature):
            msg = self.copy()
            msg.pop('signature')  # remove 'signature'
            return SecureMessage(msg)
        else:
            raise ValueError('Signature error')
