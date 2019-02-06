#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Admin module has logic about checking for admin group info."""
from __future__ import absolute_import
from json import loads
import requests
from .config import get_config

RECURSION_DEPTH = 0


# pylint: disable=too-few-public-methods
class AdminPolicy(object):
    """
    Enforces the admin policy.

    Base class for checking for admin group membership or not.
    """

    md_url = get_config().get('metadata', 'endpoint_url')
    all_users_url = '{0}/users'.format(md_url)
    all_instruments_url = '{0}/instruments'.format(md_url)
    all_proposals_url = '{0}/proposals'.format(md_url)
    prop_participant_url = '{0}/proposal_participant'.format(md_url)
    prop_instrument_url = '{0}/proposal_instrument'.format(md_url)
    inst_custodian_url = '{0}/instrument_custodian'.format(md_url)
    inst_group_url = '{0}/instrument_group'.format(md_url)

    def __init__(self):
        """Constructor for Uploader Policy."""
        self.admin_group = get_config().get('policy', 'admin_group')
        self.admin_group_id = get_config().get('policy', 'admin_group_id')

    def _format_url(self, url, **get_args):
        """Append the recursion_depth parameter to the url."""
        get_args['recursion_depth'] = RECURSION_DEPTH
        args_str = '&'.join(
            [u'{0}={1}'.format(key, value) for key, value in get_args.items()]
        )
        return u'{0}?{1}'.format(getattr(self, url), args_str)

    def _all_proposal_info(self):
        return loads(requests.get(self._format_url('all_proposals_url')).text)

    def _all_instrument_info(self):
        return loads(requests.get(self._format_url('all_instruments_url')).text)

    def _proposals_for_user(self, user_id):
        if self._is_admin(user_id):
            return [prop['_id'] for prop in self._all_proposal_info()]

        prop_url = self._format_url('prop_participant_url', person_id=user_id)
        return [part['proposal_id'] for part in loads(requests.get(prop_url).text)]

    def _proposals_for_custodian(self, user_id):
        inst_list = self._instruments_for_custodian(user_id)
        proposals_for_custodian = set([])
        for inst in inst_list:
            proposals = self._proposals_for_inst(inst)
            proposals_for_custodian = proposals_for_custodian.union(proposals)
        return list(proposals_for_custodian)

    def _instruments_for_custodian(self, user_id):
        inst_custodian_associations_url = self._format_url(
            'inst_custodian_url', custodian_id=user_id)
        inst_custodian_list = loads(requests.get(
            inst_custodian_associations_url).text)
        return [i['instrument_id'] for i in inst_custodian_list]

    def _proposals_for_inst(self, inst_id):
        inst_props_url = self._format_url(
            'prop_instrument_url',
            instrument_id=inst_id
        )
        inst_props = loads(requests.get(inst_props_url).text)
        inst_props = set([part['proposal_id'] for part in inst_props])
        return inst_props

    def _proposals_for_user_inst(self, user_id, inst_id):
        props = set(self._proposals_for_user(user_id))
        props_for_custodian = set(self._proposals_for_custodian(user_id))
        inst_groups = self._groups_for_inst(inst_id)
        if inst_groups:
            group_insts = set()
            for group_id in inst_groups:
                group_insts |= set(self._instruments_for_group(group_id))
        else:
            group_insts = set([inst_id])
        ginst_props = set()
        for ginst_id in group_insts:
            ginst_props |= self._proposals_for_inst(ginst_id)
        return list((props | props_for_custodian) & ginst_props)

    def _proposal_info_from_ids(self, prop_list):
        ret = []
        if prop_list:
            for prop_id in prop_list:
                prop_url = self._format_url('all_proposals_url', _id=prop_id)
                ret.extend(loads(requests.get(prop_url).text))
        return ret

    def _groups_for_inst(self, inst_id):
        inst_g_url = self._format_url('inst_group_url', instrument_id=inst_id)
        return [i['group_id'] for i in loads(requests.get(inst_g_url).text)]

    def _instruments_for_group(self, group_id):
        inst_g_url = self._format_url('inst_group_url', group_id=group_id)
        return [i['instrument_id'] for i in loads(requests.get(inst_g_url).text)]

    def _instruments_for_user(self, user_id):
        if self._is_admin(user_id):
            return [inst['_id'] for inst in self._all_instrument_info()]
        return self._instruments_for_custodian(user_id)

    def _instruments_for_user_prop(self, user_id, prop_id):
        user_insts = set(self._instruments_for_user(user_id))
        if self._is_admin(user_id):
            return list(user_insts)
        prop_insts_url = self._format_url(
            'prop_instrument_url', proposal_id=prop_id)
        prop_insts = set([part['instrument_id']
                          for part in loads(requests.get(prop_insts_url).text)])
        inst_groups = set()
        for inst_id in prop_insts:
            inst_groups |= set(self._groups_for_inst(inst_id))
        group_insts = set()
        for group_id in inst_groups:
            group_insts |= set(self._instruments_for_group(group_id))
        return list(group_insts | user_insts | prop_insts)

    def _instrument_info_from_ids(self, inst_list):
        ret = []
        for inst_id in inst_list:
            inst_url = self._format_url('all_instruments_url', _id=inst_id)
            ret.extend(loads(requests.get(inst_url).text))
        return ret

    def _users_for_prop(self, prop_id):
        user_prop_url = self._format_url(
            'prop_participant_url', proposal_id=prop_id)
        user_props = loads(requests.get(user_prop_url).text)
        return list(set([str(part['person_id']) for part in user_props]))

    def _user_info_from_kwds(self, **kwds):
        return loads(requests.get(self._format_url('all_users_url', **kwds)).text)

    @staticmethod
    def _object_id_valid(object_lookup_name, object_id):
        if not object_id:
            return False
        object_type_url = '{0}/{1}'.format(get_config().get('metadata', 'endpoint_url'),
                                           object_lookup_name)
        object_query_url = u'{0}?_id={1}'.format(object_type_url, object_id)
        object_value_req = requests.get(object_query_url)
        object_is_valid = loads(object_value_req.text)
        return len(object_is_valid) > 0

    def _is_admin(self, user_id):
        amember_query = '{0}/user_group?group_id={1}&person_id={2}'.format(
            self.md_url,
            self.admin_group_id,
            user_id
        )
        is_admin_req = requests.get(amember_query)
        is_admin_list = loads(is_admin_req.text)
        return len(is_admin_list) > 0
# pylint: enable=too-few-public-methods
