# -*- coding: utf-8 -*-
import json
import inspect


class VraBaseObject:
    """Base class for business models class. Use to implement basic method.
    """

    def to_dict(self, raw_data=False):
        """Return serialized object
            raw_data (bool, optional): Defaults to False. If true, also return the raw_data attribute of the object
        
        Returns:
            dict: dict of the object attribute
        """

        result = {}
        for k in inspect.signature(self.__class__).parameters:
            result[k] = getattr(self, k)

        if not raw_data:
            result.pop('raw_data')
        return result

    def to_json(self, raw_data=False):
        """Return json representation of the object
            raw_data (bool, optional): Defaults to False. If true, also return the raw_data attribute of the object
        
        Returns:
            string: json representation of the object
        """

        return json.dumps(self.to_dict(raw_data))
