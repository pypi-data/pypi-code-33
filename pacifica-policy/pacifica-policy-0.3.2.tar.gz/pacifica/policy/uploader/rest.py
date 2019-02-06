#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The CherryPy rest object for the structure."""
from json import dumps
from cherrypy import tools, request, HTTPError
from pacifica.policy.admin import AdminPolicy


# pylint: disable=too-few-public-methods
class UploaderPolicy(AdminPolicy):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = True

    @staticmethod
    def _filter_results(results, *args):
        for result in results:
            for key in list(result.keys()):
                if key not in args:
                    del result[key]

    @staticmethod
    def _clean_user_query_id(query):
        """determine the user_id for whatever is in the query."""
        try:
            return int(query['user'])
        except ValueError:
            return None

    def _user_info_from_queries(self, user_queries):
        ret = []
        for user_query in user_queries:
            ret.extend(self._user_info_from_kwds(**user_query))
        return ret

    def _query_select_user_info(self, query):
        user_id = self._clean_user_query_id(query)
        where_objects = query['where'].keys()
        user_queries = []
        if 'network_id' in where_objects:
            user_queries.append({'network_id': query['where']['network_id']})
        elif 'proposal_id' in where_objects:
            for prop_user_id in self._users_for_prop(query['where']['proposal_id']):
                user_queries.append({'_id': prop_user_id})
        else:
            user_queries.append({'_id': user_id})
        return self._user_info_from_queries(user_queries)

    def _query_select_proposal_info(self, query):
        user_id = self._clean_user_query_id(query)
        where_objects = query['where'].keys()
        if 'instrument_id' in where_objects:
            prop_ids = self._proposals_for_user_inst(
                user_id, query['where']['instrument_id'])
        elif '_id' in query['where']:
            prop_ids = [query['where']['_id']]
        else:
            prop_ids = self._proposals_for_user(user_id)
        return self._proposal_info_from_ids(prop_ids)

    def _query_select_instrument_info(self, query):
        user_id = self._clean_user_query_id(query)
        if 'proposal_id' in query['where']:
            if self._is_admin(user_id):
                return self._all_instrument_info()
            inst_ids = self._instruments_for_user_prop(
                user_id, query['where']['proposal_id'])
        elif '_id' in query['where']:
            inst_ids = [query['where']['_id']]
        else:
            inst_ids = self._instruments_for_user(user_id)
        return self._instrument_info_from_ids(inst_ids)

    def _query_select_admin(self, query):
        wants_object = query['from']
        if wants_object == 'users':
            return self._query_select_user_info(query)
        if wants_object == 'proposals':
            if '_id' in query['where']:
                prop_ids = [query['where']['_id']]
                return self._proposal_info_from_ids(prop_ids)
            return self._all_proposal_info()
        if wants_object == 'instruments':
            return self._query_select_instrument_info(query)
        raise TypeError('Invalid Query: ' +
                        'Not sure how to want {0} where {1}'.format(wants_object, query['where']))

    def _query_select(self, query):
        wants_object = query['from']
        if wants_object == 'users':
            return self._query_select_user_info(query)
        if wants_object == 'proposals':
            return self._query_select_proposal_info(query)
        if wants_object == 'instruments':
            return self._query_select_instrument_info(query)
        raise TypeError('Invalid Query: ' +
                        'Not sure how to want {0} where {1}'.format(wants_object, query['where']))

    @staticmethod
    def _valid_query(query):
        if 'user' not in query:
            return False
        if 'from' not in query:
            return False
        if 'columns' not in query:
            return False
        return True

    # pylint: disable=invalid-name
    @tools.json_out()
    @tools.json_in()
    def POST(self):
        """Read in the json query and return results."""
        query = request.json
        if not self._valid_query(query):
            raise HTTPError(500, dumps(
                {'message': 'Invalid Query.', 'status': 'error'}))
        if self._is_admin(self._clean_user_query_id(query)):
            results = self._query_select_admin(query)
        else:
            results = self._query_select(query)
        self._filter_results(results, *(query['columns']))
        return results
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
