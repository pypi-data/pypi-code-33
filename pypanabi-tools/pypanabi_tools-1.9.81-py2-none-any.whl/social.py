#!/usr/bin/env python

import facebook
import ast
import urllib
import logging


class OLXGraphAPI(facebook.GraphAPI):
    def get_objects(self, ids, service=None, **args):
        """Fetches all of the given object from the graph.

        We return a map from ID to object. If any of the IDs are
        invalid, we raise an exception.
        """
        args["ids"] = ",".join(ids)
        if service:
            return self.request(self.version + "/" + service, args)
        else:
            return self.request(self.version + "/", args)


class Facebook(object):
    def __init__(self, app_id, app_secret_id):
        """
        Constructor
        """
        self._logger = logging.getLogger(__name__)
        self._app_id = app_id
        self._app_secret_id = app_secret_id
        self._access_token = self._get_access_token(app_id=self._app_id, app_secret_id=self._app_secret_id)
        self._graph = OLXGraphAPI(access_token=self._access_token)

    def get_application_id(self):
        """
        Get application id
        :return: Application identifier [Long]
        """
        return self._app_id

    def _get_access_token(self, app_id, app_secret_id):
        """
        Get access token with app id and app secret id
        :return: Access token [String]
        """
        args = dict(client_id=app_id,
                    client_secret=app_secret_id,
                    grant_type='client_credentials')

        try:
            url = 'https://graph.facebook.com/v2.11/oauth/access_token?' + urllib.urlencode(args)
            self._logger.debug(url)
            response = urllib.urlopen(url)
            self._logger.debug(response.getcode())
            access_token = None
            if response.getcode() == 200:
                access_token = ast.literal_eval(response.read())['access_token']

            return access_token
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_users_information(self, ids, fields=None):
        """
        Get users information including general and friends information
        :param ids: List of facebook ids [List<String>]
        :param fields: Fields to retrieve separated by comma [List<String>]
        :return: Data for all users [Dictionary]
        """
        total = len(ids)
        req_ok = 0
        response_general_info = dict()
        response_friends_info = dict()
        users_data = dict()
        data = dict()

        if not fields:
            fields = 'id,name'

        self._logger.debug('Total requests: {}'.format(total))

        # General Info
        try:
            self._logger.debug('Getting general data for {} users from Facebook...'.format(len(ids)))
            response_general_info = self._graph.get_objects(ids=ids, fields=fields)
            req_ok += len(ids)
        except Exception as ex:
            self._logger.debug(repr(ex))

            # Re-trying users with errors
            self._logger.debug('Retrying to get general data for {} users from Facebook...'.format(len(ids)))
            for id in ids:
                try:
                    user_general_info = self._graph.get_object(id=id, fields=fields)

                    response_general_info[str(id)] = user_general_info
                    req_ok += 1
                except Exception as ex:
                    self._logger.debug(repr(ex))
                    continue

        # Friends Info
        try:
            self._logger.debug('Getting friends data for {} users from Facebook...'.format(len(ids)))
            response_friends_info = self._graph.get_objects(ids=ids, service='friends')
        except Exception as ex:
            self._logger.debug(repr(ex))

            # Re-trying users with errors
            self._logger.debug('Retrying to get friends data for {} users from Facebook...'.format(len(ids)))
            for id in ids:
                try:
                    user_friends_info = self._graph.get_object(id=id + '/friends', fields=fields)

                    response_friends_info[str(id)] = user_friends_info
                except Exception as ex:
                    self._logger.debug(repr(ex))
                    continue

        self._logger.debug('Requests OK = {}'.format(req_ok))
        self._logger.debug('Requests KO = {}'.format(total - req_ok))

        # Merging information
        if response_general_info:
            for user in response_general_info:
                user_info = response_general_info[user]

                if 'picture' in user_info:
                    user_info['has_profile_picture'] = int(not user_info['picture']['data']['is_silhouette'])
                else:
                    user_info['has_profile_picture'] = -1

                del user_info['picture']

                if response_friends_info:
                    if user in response_friends_info:
                        friends_info = response_friends_info[user]
                        if 'summary' in friends_info:
                            summary = friends_info['summary']

                            if 'total_count' in summary:
                                user_info['total_friends'] = summary['total_count']
                            else:
                                user_info['total_friends'] = -1
                        else:
                            user_info['total_friends'] = -1

                        user_info['friends'] = friends_info['data']
                    else:
                        user_info['total_friends'] = -1
                        user_info['friends'] = dict()
                else:
                    user_info['total_friends'] = -1
                    user_info['friends'] = dict()

                users_data[user] = user_info

        data['data'] = users_data
        data['status'] = {'total': total,
                          'ok': req_ok,
                          'ko': total - req_ok}

        self._logger.debug('DATA = {}'.format(data))

        return data





