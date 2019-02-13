"""Netbox class file."""

import netaddr
import pynetbox


class Netbox(object):
    """Netbox class."""

    def __init__(self, url, token, verbose=False):
        """Initialize the object."""
        self.token = token
        self.url = url
        self.verbose = verbose

        # connect
        self.netbox = pynetbox.api(self.url, token=self.token)

        # prefixes
        self.prefixes = self.get_prefixes()
        self.descriptions = self.get_prefix_descriptions()

        # vlans
        self.vlans = self.get_vlans()

        # groupings
        self.groupings = {}
        self.grouping_ids = {}

        # collection all grouping labels/values from all prefixes
        for pid in self.prefixes:
            prefix = self.prefixes[pid]
            grouping = prefix.custom_fields['grouping']
            if not grouping:
                continue
            value = grouping['value']
            label = grouping['label']
            self.groupings[label] = value
            self.grouping_ids[value] = label

    def check_prefix(self, prefix):
        """Check a single prefix."""
        output = []

        # check gateway
        # output.extend(self.check_gateway(prefix))

        # check grouping
        # output.extend(self.check_grouping(prefix))

        # check mab_tag
        output.extend(self.check_mab_tag(prefix))

        # check netmask
        # output.extend(self.check_netmask(prefix))

        # check servicenow_tag
        output.extend(self.check_servicenow_tag(prefix))

        # check usable range
        output.extend(self.check_usable_range(prefix))

        # check vlan
        # output.extend(self.check_vlan(prefix))

        if output:
            print('\n%s:' % (prefix.prefix))
            print('   '+'\n   '.join(output))

    def check_prefixes(self, prefixes=None):
        """Check all the prefixes for issues."""
        if not prefixes:
            prefixes = self.prefixes

        for pid in prefixes:
            prefix = prefixes[pid]
            self.check_prefix(prefix)

    def check_gateway(self, prefix):
        """Check the grouping field."""
        gateway = prefix.custom_fields.get('gateway')
        output = []
        if not gateway:
            output.append('No gateway set.')
        return output

    def check_grouping(self, prefix):
        """Check the grouping field."""
        grouping = prefix.custom_fields.get('grouping')
        output = []
        if not grouping:
            output.append('No grouping set.')
        return output

    def check_mab_tag(self, prefix):
        """Check the mab_tag field."""
        mab_tag = prefix.custom_fields.get('mab_tag')
        output = []
        if mab_tag == '-':
            output.append('Bad mab_tag value: %s' % (mab_tag))
        return output

    def check_netmask(self, prefix):
        """Check the grouping field."""
        netmask = prefix.custom_fields.get('netmask')
        output = []
        if not netmask:
            output.append('No netmask set.')
        return output

    def check_servicenow_tag(self, prefix):
        """Check the servicenow tag."""
        custom_fields = prefix.custom_fields
        servicenow_tag = prefix.custom_fields.get('servicenow_tag')

        output = []

        # return if empty
        if servicenow_tag is None:
            return output

        building, floor, network_type = self.parse_servicenow_tag(servicenow_tag)

        # make sure we have all the fields set
        if not building or not floor or not network_type:
            output.append('Bad servicenow_tag: %s' % (servicenow_tag))

        # make sure that we have a usable ip range
        usable_start_ip = custom_fields.get('usable_start_ip')
        usable_end_ip = custom_fields.get('usable_end_ip')

        if not usable_start_ip and not usable_end_ip:
            output.append('No usable start/end IP set.')
        elif not usable_start_ip:
            output.append('No usable start IP set.')
        elif not usable_end_ip:
            output.append('No usable end IP set.')

        return output

    def check_usable_range(self, prefix):
        """Check the usable range custome fields."""
        custom_fields = prefix.custom_fields

        # get start/end
        usable_start_ip = custom_fields.get('usable_start_ip')
        usable_end_ip = custom_fields.get('usable_end_ip')

        output = []
        # if not usable_start_ip and not usable_end_ip:
        #     output.append('No usable start/end IP set.')
        # elif not usable_start_ip:
        #     output.append('No usable start IP set.')
        # elif not usable_end_ip:
        #     output.append('No usable end IP set.')

        if not usable_start_ip and not usable_end_ip:
            return output

        start = None
        end = None

        # check start IP
        try:
            start = netaddr.IPAddress(usable_start_ip)
        except Exception as e:
            output.append('ERROR parsing usable start IP: %s' % (usable_start_ip))
            output.append('   %s' % (e))

        # check end IP
        try:
            end = netaddr.IPAddress(usable_end_ip)
        except Exception as e:
            output.append('ERROR parsing usable end IP: %s' % (usable_end_ip))
            output.append('   %s' % (e))

        if end < start:
            output.append('Usable end IP before start IP: %s - %s' % (
                usable_start_ip,
                usable_end_ip,
            ))

        # create an IPSet of this prefix
        prefixset = netaddr.IPSet([prefix.prefix])

        # check start/stop to make sure it's in the right range
        if start not in prefixset:
            output.append('Usable start IP not in CIDR range: %s' % (start))
        if end not in prefixset:
            output.append('Usable end IP not in CIDR range: %s' % (start))

        return output

    def check_vlan(self, prefix):
        """Check the grouping field."""
        vlan = prefix.vlan
        output = []
        if not vlan:
            output.append('No VLAN set.')
        return output

    def get_prefix_data(self, prefix):
        """Return a dict of useful info about a prefix."""
        custom_fields = prefix.custom_fields

        # get grouping
        grouping = None
        if custom_fields['grouping']:
            grouping = u'%s' % (custom_fields['grouping']['label'])

        building = None
        floor = None
        network_type = None

        # get servicenow tag
        servicenow_tag = None
        if custom_fields['servicenow_tag']:
            servicenow_tag = u'%s' % (custom_fields['servicenow_tag'])
            building, floor, network_type = self.parse_servicenow_tag(servicenow_tag)

        # get vlan (int)
        vlan = None
        if prefix.vlan:
            vlan = prefix.vlan.vid

        data = {
            'building': building,
            'description': prefix.description,
            'cidr': u'%s' % (prefix.prefix),
            'created': prefix.created,
            'floor': floor,
            'gateway': custom_fields['gateway'],
            'grouping': grouping,
            'id': prefix.id,
            'last_updated': prefix.last_updated,
            'mab_tag': custom_fields['mab_tag'],
            'mtu': custom_fields['mtu'],
            'netmask': custom_fields['netmask'],
            'network_type': network_type,
            'notes': custom_fields['notes'],
            'servicenow_tag': custom_fields['servicenow_tag'],
            'vlan': vlan,
            'usable_end_ip': custom_fields['usable_end_ip'],
            'usable_start_ip': custom_fields['usable_start_ip']
        }
        return data

    def get_prefix_descriptions(self):
        """Return a dict of Prefixes by their description."""
        descriptions = {}
        for pid in self.prefixes:
            prefix = self.prefixes[pid]
            description = prefix.description
            if description in descriptions:
                print('WARNING: Duplicate Prefix description: %s' % (description))
            descriptions[description] = prefix
        return descriptions

    def get_prefixes(self):
        """Return a dict of Prefixes in netbox."""
        prefixes = {}
        for prefix in self.netbox.ipam.prefixes.all():
            pid = prefix.id
            prefixes[pid] = prefix
        return prefixes

    def get_sheet_prefix(self, prefix):
        """Return a prefix in the format that Google Sheets creates."""
        data = self.get_prefix_data(prefix)

        sheet_data = {
            'grouping': data['grouping'],
            'description': data['description'],
            'network_type': data['network_type'],
            'building': data['building'],
            'floor': data['floor'],
            'vlan': data['vlan'],
            'vmps_tag': data['vmps_tag'],
            'cidr': data['cidr'],
            'gateway': data['gateway'],
            'netmask': data['netmask'],
            'usable_start': data['usable_start'],
            'usable_end': data['usable_end'],
            'notes': data['notes'],
        }

        for key in sheet_data:
            if not sheet_data[key]:
                if key in ['usable_start', 'usable_end']:
                    sheet_data[key] = '-'
                else:
                    sheet_data[key] = ''

        return sheet_data

    def get_vlans(self):
        """Return a dict of VLANs in netbox."""
        vlans = {}
        for vlan in self.netbox.ipam.vlans.all():
            vid = vlan.id
            vlans[vid] = vlan
        return vlans

    def parse_servicenow_tag(self, servicenow_tag):
        """Return the building, floor and network_type for a servicenow_tag."""
        building = None
        floor = None
        network_type = None

        if servicenow_tag:
            # split up the tag into three fields
            fields = servicenow_tag.split(':')

            # check that we have three
            if len(fields) == 3:
                network_type, building, floor = fields

        return building, floor, network_type
