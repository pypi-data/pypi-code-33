# -*- coding: utf-8 -*-
import importlib

from logstash import formatter


class ConfigFormatterClassMixin():
    """config formatter by class path."""

    def config_formatter(self, message_type='logstash', tags=None, fqdn=False, version=0, class_path=None):
        if class_path:
            self._config_formatter_with_classpath(
                class_path=class_path, tags=tags, fqdn=fqdn, version=version)
        else:
            if version == 1:
                self.formatter = formatter.LogstashFormatterVersion1(
                    message_type, tags, fqdn)
            else:
                self.formatter = formatter.LogstashFormatterVersion0(
                    message_type, tags, fqdn)

    def _config_formatter_with_classpath(self, class_path, *args, **kwargs):
        """Config formatter by class path.

        Arguments:
            class_path {str} -- Formatter Class Location. 
                e.g. logstash.formatter.LogstashFormatterVersion0
        """
        module_path, class_name = class_path.rsplit('.', 1)
        formatter_cls = getattr(
            importlib.import_module(module_path), class_name)
        self.formatter = formatter_cls(*args, **kwargs)
