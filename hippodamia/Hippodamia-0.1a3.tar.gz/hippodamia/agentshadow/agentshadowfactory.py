from hippodamia.agentshadow.agentshadow import AgentShadow


class AgentShadowFactory:
    _topics = None
    _timings = None
    _update_available = None
    _mongo_client = None
    _mqtt_client = None
    _logger = None

    def __init__(self, topics, timings, update_available, mongo_client, mqtt_client, logger):
        self._topics = topics
        self._timings = timings
        self._update_available = update_available
        self._mongo_client = mongo_client
        self._mqtt_client = mqtt_client
        self._logger = logger

    def create_agentshadows(self, preload_config_list):
        shadows = {}

        for preload_config in preload_config_list:
            gid = str(preload_config["gid"])
            shadow = self.new_agentshadow(preload_config=preload_config)
            shadows[gid] = shadow

        return shadows

    def new_agentshadow(self, preload_config=None, gid=None):
        if preload_config is None and gid is None:
            raise ValueError("AgentShadowFactory.create_agentshadow - preload_config and gid are None")
        shadow = AgentShadow(self._topics, self._timings, self._update_available, self._mongo_client, self._mqtt_client,
                             self._logger, preload_config=preload_config, gid=gid)
        return shadow
