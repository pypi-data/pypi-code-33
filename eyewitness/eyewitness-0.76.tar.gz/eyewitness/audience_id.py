import arrow
import six
from abc import ABCMeta, abstractmethod


class AudienceId(object):
    """
    the target of AudienceId is used to standardize the AudienceId format,
    """

    def __init__(self, platform_id, user_id):
        """
        Parameters
        ----------
        platform_id: str
            platform_id of feedback user from
        user_id: str
            id of feedback user
        """
        self.platform_id = platform_id
        self.user_id = user_id

    def __hash__(self):
        return hash(self.platform_id) ^ hash(self.user_id)

    def __str__(self):
        # TODO make a more safer way
        return "{}::{}".format(self.platform_id, self.user_id)

    def __eq__(self, other):
        if isinstance(other, AudienceId):
            return str(self) == str(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, AudienceId):
            return str(self) < str(other)
        return NotImplemented

    @classmethod
    def from_str(cls, audience_id_str):
        """
        Parameters
        ----------
        audience_id_str: str
            a string with pattern {platform}::{audience_id} e.g: "line::minhan_hgdfmjg2715".

        Returns
        -------
        audience_id: AudienceId
            a AudienceId obj
        """
        # TODO make a more safer way
        platform_id, user_id = audience_id_str.split('::')
        return cls(platform_id=platform_id, user_id=user_id)


@six.add_metaclass(ABCMeta)
class AudienceRegister():
    """
    Abstract Class for handling audience registration
    """
    def register_audience(self, audience_id, meta_dict):
        """
        register audience

        Parameters
        ----------
        audience_id: AudienceId
            audience information
        meta_dict: dict
            additional information
        """
        register_time = meta_dict.get('register_time', arrow.now().timestamp)
        description = meta_dict.get('description', '')
        self.insert_registered_user(audience_id, register_time, description)

    @abstractmethod
    def insert_registered_user(self, audience_id, register_time, description):
        """
        abstract method for register audience id
        """
        pass
