#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Message:
    """
    Represents a message that is serialized to json as {'type':..., 'payload':...}
    """

    def __init__(self, message_type, payload):
        if message_type is None:
            raise ValueError('message_type cannot be None!')

        if payload is None:
            raise ValueError('payload cannot be None!')

        if not isinstance(payload, dict):
            raise ValueError('payload must be a type of dict')

        self.type = message_type
        self.payload = payload
