# -*- coding: utf-8 -*-
import inspect
import json


class Constant(object):
    _all_constants_dict = []
    _constants = []

    @classmethod
    def _cache_vals(cls):

        # save attributes to _constants on first call
        # so no iteration is needed later

        attrs = []
        for attr_name, attr in cls.__dict__.items():

            # Constant class can also have nested constant classes
            if inspect.isclass(attr):

                try:
                    attrs.extend(attr.get_all())

                except AttributeError:
                    raise AttributeError(
                        'Constant class children should be Constant'
                        'not object or some other type')
            else:

                if attr_name.isupper() and not attr_name.startswith('__'):
                    attrs.append(attr)

        cls._constants = attrs
        
    @classmethod
    def get_all(cls):

        if not cls._constants:
            cls._cache_vals()

        # if you need orderging of get_all() results, override this method
        return cls._constants

    @classmethod
    def __get_val(cls, val, attr):

        if not cls._constants:
            cls._cache_vals()

        if val not in cls.__dict__['_constants']:
            raise AttributeError('Constant class "%s" has no attribute "%s"' % (cls.__name__, val))

        try:
            return getattr(cls, attr)[val]
        except KeyError:
            raise KeyError('Constant "%s.%s" missing requested key "%s"' % (
                cls.__name__, attr, val))

    @classmethod
    def get_title(cls, val, short=False):
        return cls.__get_val(val, '_short_titles' if short else '_titles')

    @classmethod
    def get_description(cls, val):
        return cls.__get_val(val, '_descriptions')

    @classmethod
    def get_all_constants(cls):
        # Returns all constant childs!
        if not cls._all_constants_dict:
            cls._all_constants_dict = {
                x.__name__: x for x in Constant.__subclasses__()
            }
        return cls._all_constants_dict

    @classmethod
    def get_safe_json_dict(cls):
        '''
        Use this to inject the constant into javasciprt
        '''
        result = {}
        for key, value in cls.__dict__.items():

            # ignore pythons internal things
            if not key.startswith('_') and not key.startswith('__'):

                try:
                    # We want only 'jsonable' things
                    json.dumps(value)
                    result[key] = value
                except:
                    # Ignore the rest!
                    pass
        return result

    @classmethod
    def to_json(cls):
        return json.dumps(cls.get_safe_json_dict())

    @classmethod
    def to_select_options(cls, prepend_string='', alphabetic_order=False, value_key='value', title_key='label'):
        # transforms constant class get_all() results to the structure
        # sutable for <select ng-options...
        try:
            opts = [{
                title_key: u'%s%s' % (prepend_string, cls.get_title(x)),
                value_key: x
            } for x in cls.get_all()]

            if alphabetic_order:
                opts = sorted(opts, key=lambda k: k['label'])
            return opts

        except AttributeError as e:

            raise Exception(
                'Probably no get_all() or get_title() '
                'implemented for %s (%s)' % (cls, e))
