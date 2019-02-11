"""Manage a resultset thatrformatter will understand"""

import logging
import sys
import collections
import types

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

DEFAULT ="\033[0m"
BOLD    ="\033[1m"


class Results(object):
    """
    Collection of ResultSet objects with focus on initialization flexibility
    """
    def __init__(self, result_sets=None, config=None):
        self.setCount = 0
        self.converter = None # TODO add plugin support to convert common result frameworks
        self._manageconfig(config)
        self._initresultsets(result_sets)

    def _initresultsets(self, result_sets):
        """
        Determine what type of resultsets were passed in handle accordingly.
        Supports list, generator, or iterator
        """
        if type(result_sets) is types.GeneratorType:
            self.generate_resultsets = result_sets
            return 
        if result_sets is None:
            result_sets = []
        try:
            self.generate_resultsets = (row for row in result_sets) # generator 
        except TypeError:
            raise TypeError("Result resultset must be iterable")

    def _manageconfig(self, opts):
        """
        Validate config for resultset
        """
        if opts is None:
            opts = {}
        if type(opts) != dict:
            raise TypeError("config for Result needs to be dict type")
        self.config = dict(opts)




    #def intialize_resultsets(self)


class ResultSet(object):
    """
    Single set of results containing row objects
    """
    def __init__(self, results, headers=None, order_map=None):
        if order_map:
            self.order_map = self._sort_order_map(order_map)
        else:
            self.order_map = order_map
        self.headers, self.header_source = self._manageheaders(headers)
        self.rowdef = collections.namedtuple("RsRow", self.headers, verbose=False, rename=True)
        self.generate_rows = None
        self.rows = []
        self.errors = []
        self.row_count = 0
        self.error_count = 0
        #self.results = results
        self._initresults(results)
        self.initialize_rows()


    def _initresults(self, results):
        """
        Determine what was type results were passed and handle accordingly.
        """
        if type(results) is types.GeneratorType:
            self.generate_rows = results
            return
        try:
            self.generate_rows = (row for row in results) # generator 
        except TypeError:
            raise TypeError("ResultSet results must be iterable")

    def initialize_rows(self):
        """
        Process rows from a generator object
        """
        for row in self.generate_rows:
            #log.debug("processing row: %s" % (row))
            self.addrow(row)
        log.debug("rows: %s, rowcount: %s, errors: %s, errorcount: %s" % (len(self.rows), self.row_count, self.errors, self.error_count))

    def addrow(self, row):
        """
        Add a single row to resultset
        """
        try:
            self.rows.append(Row(row, self.rowdef))
            self.row_count += 1
        except:
            self.errors.append(row)
            self.error_count += 1

        
    def _manageheaders(self, headers):
        """
        Type checking for headers and order map provided to result set
        """
        if self.order_map is not None and headers is not None:
            # use headers if both are provided
            #raise TypeError("ResultSet() requires and order_map or headers, not both")
            if type(headers) != list:
                raise TypeError("ResultSet() requires headers as list when no order_map provided")
            else:
                return list(headers), "headers priority"
        if self.order_map is None:
            if headers is None:
                raise TypeError("ResultSet() requires headers or order_map (neither given)")
            elif type(headers) != list:
                raise TypeError("ResultSet() requires headers as list when no order_map provided")
            else:
                return headers, "headers"
        if headers is None:
            if type(self.order_map) != collections.OrderedDict:
                raise TypeError("ResultSet() requires order_map as dict with no headers. provided:  type(self.order_map)")
            else:
                return list(self.order_map.values()), "order_map"
    
    @staticmethod
    def _sort_order_map(order_map):
        """
        returns and ordered dict of keys based on an order_map dict with floats/ints as keys
        """
        if type(order_map) != dict:
            raise TypeError("must provide dict to define ordermapping as '{float: key_string}'. provided %s" % order_map)
        try:
            converted_keys = [(k, float(k)) for k in order_map.keys()]
        except ValueError as e:
            print("ValueError: {0}".format(e))
            print("%s[TIP]%s     : check that all keys provided in order map can be converted to floats" % ('\033[1m', '\033[0m'))
            raise

        return collections.OrderedDict([(ck, order_map[k]) for k, ck in sorted(converted_keys, key=lambda x: x[1])])

            
    
class Row(object):
    """
    Row of data that can be initialized from tuple, list, dict
    """
    __slots__ = ('data')
    def __init__(self, values, rowdef=None):
        self.data = self._normalize_row(values, rowdef)

    def rowdef(self):
        return self.data._fields

    @staticmethod
    def _normalize_row(values, rowdef):
        """
        return a named tuple of values if provided bounded iterable dict, tuple, etc
        """
        tp = type(values)
        if tp == list:
            return rowdef._make(values)
        elif tp == tuple:
            return rowdef._make(values)
        elif tp == dict:
            # filtered is a new dict only the named fields of the rowdef
            filtered = { k: values.get(k, None) for k in rowdef._fields }
            return rowdef(**filtered)
        else:
            raise TypeError("must provide values as bounded iterable for new Row")



if __name__ == "__main__":
    log.info("testing logger in main")

