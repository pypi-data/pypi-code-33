from alcathous.algorithms.average import Average
from alcathous.algorithms.weightedaverage import WeightedAverage
from alcathous.algorithms.count import Count
from alcathous.algorithms.minimum import Minimum
from alcathous.algorithms.maximum import Maximum
from pelops import mylogger


class AlgorithmFactory:
    """
    Create algorithm instances based on the given yaml config structure.

    Note: each implementation of abstractalgorithm must be represented by a class variable. E.g. the implementation
    'Average' is added with the line 'avg = Average'. 'avg' represents the identifier that must be used in the
    config yaml.
    """

    avg = Average  # used by the line "klass = cls.__dict__[class_name]"
    wavg = WeightedAverage  # used by the line "klass = cls.__dict__[class_name]"
    count = Count  # used by the line "klass = cls.__dict__[class_name]"
    min = Minimum  # used by the line "klass = cls.__dict__[class_name]"
    max = Maximum  # used by the line "klass = cls.__dict__[class_name]"

    @classmethod
    def get_instance(cls, name, config, parent_logger, data_set, lock_data_set, topic_pub_prefix, mqtt_client,
                     no_data_behavior):
        """
        Generate a method / algorithm instance.

        :param name: Name of the to be created method / algorithm instance.
        :param config: Configuration yaml containing config for all algorithms.
        :param parent_logger: logger instance from the parent.
        :param data_set: the data the algortihm should work with
        :param lock_data_set: the algorithm works with the data set only if a lock has been acquired successfully
        :param topic_pub_prefix: prefix+name is the topic the result will be published to
        :param mqtt_client: instance of an mymqttclient
        :param no_data_behavior: defines how the algorithm should react if no data is available.
        :return: The corresponding method / algorithm instance
        """
        _logger = mylogger.get_child(parent_logger, cls.__name__)
        class_name = str(config["algorithm"]).lower()
        try:
            klass = cls.__dict__[class_name]
        except KeyError:
            raise ValueError("Unknown value for AlgorithmFactory '{}'. Expected {}.".
                             format(class_name, cls.__dict__.keys()))
        _logger.info("AlgorithmFactory.get_instance - creating instance of '{}'.".format(klass.__name__))
        instance = klass(name, config, parent_logger, data_set, lock_data_set, topic_pub_prefix, mqtt_client,
                         no_data_behavior)
        return instance

    @classmethod
    def get_instances(cls, method_names, config_methods, parent_logger, data_set, lock_data_set, topic_pub_prefix,
                      mqtt_client, no_data_behavior):
        """
        Take the list of method names and generates the corresponding algorithm instances.

        :param method_names: List of algorithms that should be generated.
        :param config_methods: Configuration yaml containing config for all algorithms.
        :param parent_logger: logger instance from the parent.
        :param data_set: the data the algortihm should work with
        :param lock_data_set: the algorithm works with the data set only if a lock has been acquired successfully
        :param topic_pub_prefix: prefix+name is the topic the result will be published to
        :param mqtt_client: instance of an mymqttclient
        :param no_data_behavior: defines how the algorithm should react if no data is available.
        :return: List of methods / algorithm instances
        """
        _logger = mylogger.get_child(parent_logger, cls.__name__)
        _logger.info("AlgorithmFactory.get_instances - creating instances of '{}'.".format(method_names))
        _logger.debug("AlgorithmFactory.get_instances - config_methods '{}'.".format(config_methods))
        methods = []
        for name in method_names:
            try:
                config = config_methods[name]
            except KeyError:
                raise ValueError("Unknown value for method '{}'. Expected {}.".
                                 format(name, config_methods.keys()))
            m = AlgorithmFactory.get_instance(name, config, parent_logger, data_set, lock_data_set,
                                              topic_pub_prefix, mqtt_client, no_data_behavior)
            methods.append(m)
        _logger.info("AlgorithmFactory.get_instances - created {} instances.".format(len(methods)))
        return methods
