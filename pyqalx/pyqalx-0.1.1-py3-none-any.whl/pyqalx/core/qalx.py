"""
.. autoclass:: Qalx
    :members:
"""
import json
import platform
import sys
import logging
from inspect import getmembers, getmro, isclass

from pyqalx.config import UserConfig, BotConfig
from pyqalx.core import QalxNoGUIDError
from pyqalx.core.bot import Bot
from pyqalx.core.entity import QalxEntity
from pyqalx.core.errors import QalxError, \
    QalxEntityNotFound, QalxMultipleEntityReturned, \
    QalxConfigError, QalxAPIResponseError, QalxNoQueueFoundByName
from pyqalx.core.group import Group
from pyqalx.core.item import Item
from pyqalx.core.queue import Queue
from pyqalx.core.set import Set
from pyqalx.transport import PyQalxAPI
from pyqalx.core.log import configure_logging, LOGGING_DEFAULTS

logger = logging.getLogger(__name__)


def entity_by_string(entity_type_name):
    def is_named_entity(o):
        if isclass(o):
            is_qalx_entity = QalxEntity in getmro(o)
            name_matches = getattr(o, "entity_type", None) == entity_type_name
            return is_qalx_entity and (name_matches)
        else:
            return False

    entity_classes = getmembers(sys.modules[__name__], is_named_entity)
    if len(entity_classes) == 0:
        raise QalxEntityNotFound(entity_type_name + " not found.")
    elif len(entity_classes) >= 2:
        raise QalxMultipleEntityReturned(entity_type_name + " matches more than 1 class.")
    else:
        return entity_classes[0][1]


class BaseQalx:

    def __init__(self):
        super().__init__()

    def get_context(self):
        return dict(
            TOKEN="",
            QALX_API_FAIL_SILENT=False,  # if True then API calls which throw HTTP errors won't raise exceptions
            MSG_WAITTIMESECONDS=20,  # calls to the remote queue will not return for this long
            MSG_BLACKOUTSECONDS=30,  # messages must be removed from the queue within this time after reading
            LOGGING_LEVEL=LOGGING_DEFAULTS['LEVEL'], # What level we should log at by default
            LOGGING_CONFIG_PATH=LOGGING_DEFAULTS['CONFIG_PATH'], # The path to a custom logging dictConfig
            LOG_FILE_PATH=LOGGING_DEFAULTS['LOG_FILE_PATH'] # The path where log files will be stored
        )


class Qalx(BaseQalx):

    def __init__(self, profile_name="default", bot_config=None, skip_ini=False):
        """main interface for operations against the qalx REST API

        :param profile_name: user profile name (default="default")
        :type profile_name: basestring
        :param bot_config: a bot config if authenticating as a bot
        :type bot_config: pyqalx.config.BotConfig
        """
        super(Qalx, self).__init__()
        self.config = UserConfig(defaults=self.get_context())
        if not skip_ini:
            self.config.from_inifile(profile_name)
        if bot_config is None:
            self.bot_config = {}
            config = self.config
        elif isinstance(bot_config, BotConfig):
            self.bot_config = bot_config
            config = self.bot_config
        else:
            raise QalxConfigError("A bot_config was supplied but it wasn't a pyqalx.config.BotConfig")

        configure_logging(config)
        self.rest_api = PyQalxAPI(config)

    def _process_api_request(self, method, *args, **kwargs):
        """calls to pyqalxapi

        :param method: http method required
        :param args: args to be passed to endpoint method
        :param kwargs: kwargs to be passed to endpoint method
        :returns: `dict` containing API resource data
        """
        if kwargs.get('meta', None) is None:
            # meta is optional but must always be sent through as a dict
            kwargs['meta'] = {}

        try:
            json.dumps(kwargs)
        except (TypeError, OverflowError):
            raise QalxError("One of the keyword arguments is not JSON serializable")

        try:
            endpoint = getattr(self.rest_api, method.lower())
        except AttributeError:
            raise Exception(f"{method} not recognised.")

        if kwargs.get("file_path"):
            file_path = kwargs.pop("file_path")
            success, data = endpoint(*args, file_path=file_path, json=kwargs)
        else:
            success, data = endpoint(*args, json=kwargs)

        if success:
            return data
        elif not self.config.getboolean("QALX_API_FAIL_SILENT"):
            m = "API request error, message:\n\n-vvv-\n\n"
            m += "\n".join([f"{k}: {v}" for k, v in data.items()])
            m += "\n\n-^^^-"
            raise QalxAPIResponseError(m)
        else:
            pass

    def get_entity_by_guid(self, entity_type, entity_guid):
        """single entity returned by its guid

        :param entity_type: name of entity type e.g. `"set"`
        :type entity_type: str
        :param entity_guid: guid of entity
        :type entity_guid: str
        :type entity_guid: uuid.UUID
        :return: a pyqalx.core.entity.QalxEntity
        """
        endpoint = f"{entity_type}/{entity_guid}"
        rest_api_get = self._process_api_request('get', endpoint)
        class_by_string = entity_by_string(entity_type)
        return class_by_string(
            rest_api_get
        )

    def archive_entity_by_guid(self, entity_type, entity_guid):
        """single entity marked as archived by its guid

        :param entity_type: name of entity type e.g. `"set"`
        :type entity_type: str
        :param entity_guid: guid of entity
        :type entity_guid: str
        :type entity_guid: uuid.UUID
        :return: a pyqalx.core.entity.QalxEntity
        """
        endpoint = f"{entity_type}/{entity_guid}/archive"
        rest_api_get = self._process_api_request('patch', endpoint)
        class_by_string = entity_by_string(entity_type)
        return class_by_string(
            rest_api_get
        )

    def save_entity(self, entity):
        """save changes to a QalxEntity

        :param entity: the entity to save
        :type entity_type: pyqalx.core.entity.QalxEntity

        """
        if not entity.get("guid"):
            raise QalxNoGUIDError("No guid.")
        endpoint = f"{entity.entity_type}/{entity['guid']}"

        keys_to_save = {k: entity[k] for k in entity if k not in ('info', 'guid')}
        rest_api_patch = self._process_api_request('patch', endpoint, **keys_to_save)
        class_by_string = entity_by_string(entity.entity_type)
        return class_by_string(
            rest_api_patch
        )

    def add_item_data(self, data=None, meta=None):
        """adds a dict of data to qalx with optional metadata

        :param data: dictionary of data
        :param meta: (optional) additional data about the item
        :return: pyqalx.core.Item
        """
        if isinstance(data, dict):
            response = self._process_api_request('post', 'item', data=data, meta=meta)
            item = Item(response)
            return item
        else:
            raise QalxError(
                "Only item data in dict format can be added with this function. To add a file try add_item_file ")

    def add_item_file(self, file_path, data=None, meta=None):
        """adds a file to qalx with optional data and metadata

        :param file: path to file
        :param data: (optional) data associated with the file
        :param meta: (optional) additional data about the item
        :return: pyqalx.core.Item
        """
        if data is None:
            data = {}
        response = self._process_api_request('post', 'item', data=data, file_path=file_path, meta=meta)
        return Item(response)

    def add_set(self, items, meta=None):
        """adds a set to qalx with the specified items

        :param items: a sequence of pyqalx.core.Item
        :param meta: (optional) additional data about the item
        :return: pyqalx.core.Set
        """
        item_guids = [item['guid'] for item in items]
        response = self._process_api_request('post', 'set', item_guids=item_guids, meta=meta)
        return Set(response)

    def add_group(self, sets, meta=None):
        """adds a group to qalx with the specified sets

        :param sets: a sequence of pyqalx.core.Set
        :param meta: (optional) additional data about the item
        :return: pyqalx.core.Group
        """
        set_guids = [dataset['guid'] for dataset in sets]

        response = self._process_api_request('post', 'group', set_guids=set_guids, meta=meta)
        return Group(response)

    @property
    def _queue_params(self):
        return {
            'VisibilityTimeout': int(self.config['MSG_BLACKOUTSECONDS'])
            }

    def add_queue(self, queue_name, meta=None):
        """adds a queue to qalx

        :param queue_name: a string identifying the queue
        :param parameters: (optional) additional configuration options for the queue
        :param meta: (optional) additional data about the item
        :return: pyqalx.core.Queue
        """
        if meta is None:
            meta = {"queue_name": queue_name}
        else:
            meta["queue_name"] = queue_name

        response = self._process_api_request('post', 'queue', parameters=self._queue_params, meta=meta)
        return Queue(response)

    def list_entities(self, entity_name, sort=None, skip=0, limit=25, **kwargs):
        """list qalx entities

        :param entity_name: type of entity to list (item, set, etc.)
        :param query_filter: (optional) meta/info key-values to filter by
        :param sort: (optional) meta/info keys to sort by
        :param skip: (default=0) number of records to skip for pagination
        :param limit: (default=25) maximum number of records to return
        :return: list of pyqalx.core.Queue
        """

        entities = self._process_api_request('get', entity_name, sort=sort, skip=skip, limit=limit, **kwargs)

        return [entity_by_string(entity_name)(e) for e in entities['data']]

    def get_queue_messages(self, queue_entity):
        """

        :param queue_entity: the queue to get messages from
        :type queue_entity: pyqalx.core.queue.Queue
        :return:
        """
        if not self.bot_config:
            raise QalxError("Only bots can get messages from queues.")
        max_msgs = int(self.bot_config.get("Q_MSGBATCHSIZE", 1))
        visibility = int(self.bot_config.get("MSG_BLACKOUTSECONDS", 30))
        waittime = int(self.bot_config.get("MSG_WAITTIMESECONDS", 20))
        message = queue_entity.get_messages(max_msgs, visibility, waittime)
        return message

    def get_queue_by_name(self, name):
        """a single queue by name

        :param name: name of queue
        :return: pyqlax.core.Queue
        :raises: pyqalx.errors.QalxReturnedMultipleError
        """

        queues = self.list_entities('queue', meta=[f"queue_name={name}"])
        if len(queues) > 1:
            queues_str = "\n".join([str(q) for q in queues])
            raise QalxMultipleEntityReturned("Expected one but got {}:\n{}".format(len(queues), queues_str))
        elif queues:
            queue = self.get_entity_by_guid('queue', queues[0]['guid'])
            return queue
        else:
            raise QalxNoQueueFoundByName(name + 'not found')

    def get_or_create_queue(self, queue_name, meta=None):
        """

        :param queue_name:
        :type queue_name: str
        :return: pyqalx.core.Queue
        """
        try:
            return self.get_queue_by_name(queue_name)
        except QalxNoQueueFoundByName:
            return self.add_queue(queue_name, meta)

    @property
    def _host_info(self):
        return {
            "node": platform.node(),
            "platform": platform.platform(),
            # TODO: add more platform and IP address infos
        }

    def add_bot(self, bot_config, meta=None):
        """adds a bot resource

        .. note::
            this should only be called by a Bot during startup not by a user directly.

        :param bot_config: the configuration settings for the bot
        :type bot_config: dict
        :param meta: (optional) additional data about the item
        :return: pyqalx.core.Bot
        """
        response = self._process_api_request('post', 'bot',
                                             config=dict(bot_config),
                                             host=self._host_info,
                                             meta=meta)
        return Bot(response)

    def update_bot_status(self, bot_guid, status):
        """updates the status on a bot

        :param bot_guid: the guid of the bot
        :param status: status information to save
        :type status: dict
        :return:
        """
        endpoint = f"bot/{bot_guid}"
        status = self._process_api_request('patch', endpoint, status=status)

