"""

"""
from . import attribute_pb2
from . import gobgp_pb2_grpc
from . import gobgp_pb2
from gobgp_client.exceptions import *

import grpc

from google.protobuf.any_pb2 import Any

IPV4_UNICAST = tuple([1, 1])
L3VPN_IPV4_UNICAST = tuple([1, 128])

WELLKNOWNCOMMUNITY = {
    'no-export': 4294967041,
    'no-advertise': 4294967042,
    'no-export-subconfed': 4294967043,
}


class GoBGPgRPCClient(object):
    """

    """
    def __init__(self, host, port, timeout):
        """

        :param host:
        :param port:
        :param timeout:
        """
        # todo write secure channel also
        self._host = host
        self._port = str(port)
        self._channel = grpc.insecure_channel(self._host + ':' + self._port)
        self._stub = gobgp_pb2_grpc.GobgpApiStub(self._channel)
        self._timeout = float(timeout)

    @staticmethod
    def parse_community(community):
        """
        Parse community from string or int and return int
        :param community:
        :return:
        """
        result = None
        if community in WELLKNOWNCOMMUNITY:
            return WELLKNOWNCOMMUNITY[community]
        try:
            _h, _l = (community.split(':'))
            result = int('{:04x}{:04x}'.format(int(_h), int(_l)), 16)
        except ValueError:
            return result
        return result

    def prep_path(self, network, origin=2, nexthop='0.0.0.0', aspath='', afi=1, safi=1, comm=[], rd=None, rt=None, vrf=None, label=0):
        """

        :param network:
        :param origin:
        :param nexthop:
        :param aspath:
        :param afi:
        :param safi:
        :param comm:
        :param rd:
        :param rt:
        :param vrf:
        :param label:
        :return:
        """
        # check netowork format
        prefix, prefix_len = tuple(network.split('/'))
        prefix_len = int(prefix_len)
        # pack mandatory attributes for any afi safi
        _origin = Any()
        _origin.Pack(attribute_pb2.OriginAttribute(origin=origin))
        _as_path = Any()
        if aspath:
            # todo split aspath to sements and pack sigments
            as_segment = attribute_pb2.AsSegment(numbers=[])
            as_segment.type = 2
            _as_path.Pack(attribute_pb2.AsPathAttribute(segments=[as_segment]))
        else:
            _as_path.Pack(attribute_pb2.AsPathAttribute(segments=[]))
        _nexthop = Any()
        _nexthop.Pack(attribute_pb2.NextHopAttribute(next_hop=nexthop))
        int_comm_list = []
        if comm:
            for str_comm in comm:
                int_comm = self.parse_community(str_comm)
                int_comm_list.append(int_comm)
            _comm = Any()
            _comm.Pack(attribute_pb2.CommunitiesAttribute(communities=int_comm_list))
        if tuple([afi, safi]) == IPV4_UNICAST:
            nlri = Any()
            nlri.Pack(attribute_pb2.IPAddressPrefix(prefix_len=prefix_len, prefix=prefix))
            attributes = [_origin, _as_path, _nexthop]
            if int_comm_list:
                attributes.append(_comm)
            path = gobgp_pb2.Path(nlri=nlri, pattrs=attributes, family=gobgp_pb2.Family(afi=afi, safi=safi))
            return path
        elif tuple([afi, safi]) == L3VPN_IPV4_UNICAST:
            # todo check rd
            _rd = Any()
            # suuport as-number:number or  ip-address:number
            if rd:
                _admin, _assigined = tuple(rd.split(':'))
            else:
                # rise except
                pass
            if '.' in _admin:
                # there is ip-address:number
                _rd.Pack(attribute_pb2.RouteDistinguisherIPAddress(admin=_admin, assigned=int(_assigined)))
            else:
                _rd.Pack(attribute_pb2.RouteDistinguisherTwoOctetAS(admin=int(_admin), assigned=int(_assigined)))
            nlri = Any()
            nlri.Pack(
                attribute_pb2.LabeledVPNIPAddressPrefix(prefix_len=prefix_len, prefix=prefix, labels=[label], rd=_rd))
            # todo get rt_attrs from rt
            _rt = Any()
            # suuport subtype 1 or 2 as:number or ip: number
            if rt:
                route_targets = []
                for one_rt in rt:
                    _rt = Any()
                    ga, la = tuple(one_rt.split(':'))
                    if '.' in ga:
                        sub_type = 2
                        _twoocas = attribute_pb2.IPv4AddressSpecificExtended(is_transitive=True,
                                                                             sub_type=sub_type,
                                                                             address=ga,
                                                                             local_admin=int(la))
                        _rt.Pack(_twoocas)
                    else:
                        sub_type = 2
                        _twoocas = attribute_pb2.TwoOctetAsSpecificExtended(is_transitive=True,
                                                                            sub_type=sub_type,
                                                                            local_admin=int(la))
                        setattr(_twoocas, 'as', int(ga))
                        _rt.Pack(_twoocas)
                    route_targets.append(_rt)
            else:
                # raise except
                pass
            extcommunities = Any()
            extcommunities.Pack(attribute_pb2.ExtendedCommunitiesAttribute(communities=route_targets))
            attributes = [_origin, _nexthop, _as_path, extcommunities]
            if int_comm_list:
                attributes.append(_comm)
            path = gobgp_pb2.Path(family=gobgp_pb2.Family(afi=afi, safi=safi), nlri=nlri, pattrs=attributes)
            return path

    def add_path(self, network, origin=2, nexthop='0.0.0.0', aspath='', afi=1, safi=1, comm=[], rd=None, rt=None, vrf=None, label=0):
        """

        :param network:
        :param origin:
        :param nexthop:
        :param aspath:
        :param afi:
        :param safi:
        :param rd:
        :param rt:
        :param vrf:
        :param label:
        :return:
        """
        path = self.prep_path(network,
                              origin=origin,
                              nexthop=nexthop,
                              aspath=aspath,
                              afi=afi, safi=safi,
                              rd=rd,
                              rt=rt,
                              vrf=vrf,
                              label=label)
        # todo add try
        result = self._stub.AddPath(gobgp_pb2.AddPathRequest(table_type=gobgp_pb2.GLOBAL, path=path), self._timeout)

    def del_path(self, network, origin=2, nexthop='0.0.0.0', aspath='', afi=1, safi=1, comm=[], rd=None, rt=None, vrf=None, label=0):
        """

        :param network:
        :param origin:
        :param nexthop:
        :param aspath:
        :param afi:
        :param safi:
        :param rd:
        :param rt:
        :param vrf:
        :param label:
        :return:
        """
        path = self.prep_path(network,
                              origin=origin,
                              nexthop=nexthop,
                              aspath=aspath,
                              afi=afi, safi=safi,
                              comm=comm,
                              rd=rd,
                              rt=rt,
                              vrf=vrf,
                              label=label)
        # todo add try..
        result = self._stub.DeletePath(gobgp_pb2.DeletePathRequest(table_type=gobgp_pb2.GLOBAL, path=path), self._timeout)

    def add_path_batch(self, networks, origin=2, nexthop='0.0.0.0', aspath='', afi=1, safi=1, comm=[], rd=None, rt=None, vrf=None, label=None):
        """

        :param networks:
        :param origin:
        :param nexthop:
        :param aspath:
        :param afi:
        :param safi:
        :param rd:
        :param rt:
        :param vrf:
        :param label:
        :return:
        """
        # make generator for stream grpc message
        def gen_path(networks, origin=2, nexthop='0.0.0.0', aspath='', afi=1, safi=1, comm=[], rd=None, rt=None, vrf=None, label=None):
            paths = []
            for network in networks:
                path = self.prep_path(network,
                                      origin=origin,
                                      nexthop=nexthop,
                                      aspath=aspath,
                                      afi=afi, safi=safi,
                                      comm=comm,
                                      rd=rd,
                                      rt=rt,
                                      vrf=vrf,
                                      label=label)
                paths.append(path)
            req = gobgp_pb2.AddPathStreamRequest(table_type=gobgp_pb2.GLOBAL, paths=paths)
            yield req
        # fill the generator
        path_iter = gen_path(networks,
                             origin=origin,
                             nexthop=nexthop,
                             aspath=aspath,
                             afi=afi, safi=safi,
                             comm=comm,
                             rd=rd,
                             rt=rt,
                             vrf=vrf,
                             label=label)
        # make addstream request
        result = self._stub.AddPathStream(path_iter, self._timeout)

    def get_table(self, rtype=0, name='', afi=1, safi=1):
        """ Get rib table from gobgpd
        :param rtype:  table type one of:
            GLOBAL = 0;
            LOCAL = 1;
            ADJ_IN = 2;
            ADJ_OUT = 3;
            VRF = 4;
        :param name: vrf name or neighbor address
        :param afi: address family id
        :param safi: sub address family id
        :type int
        :type str
        :type int
        :type int
        :return: list of {'prefix': '', 'prefix_len': '', 'origin': '', 'nexthop': '', 'aspath': [], 'attributes': []}
        :rtype list
        """

        path = {'prefix': '', 'prefix_len': '', 'origin': '', 'nexthop': '', 'aspath': [], 'attributes': [], 'rt': []}
        table = []
        result = self._stub.ListPath(gobgp_pb2.ListPathRequest(table_type=rtype,
                                                               name=name,
                                                               family=gobgp_pb2.Family(afi=afi, safi=safi),
                                                               prefixes=[]))
        if tuple([afi, safi]) == L3VPN_IPV4_UNICAST:
            for msg in result:
                _path = msg.destination.paths[0]
                path = {
                    'prefix': '',
                    'prefix_len': '',
                    'origin': '',
                    'nexthop': '',
                    'aspath': [],
                    'attributes': [],
                    'rt': []
                }
                if _path.nlri.Is(attribute_pb2.LabeledVPNIPAddressPrefix.DESCRIPTOR):
                    labledvpnv4 = attribute_pb2.LabeledVPNIPAddressPrefix()
                    _path.nlri.Unpack(labledvpnv4)
                    path['prefix'] = labledvpnv4.prefix
                    path['prefix_len'] = labledvpnv4.prefix_len
                    if labledvpnv4.rd.Is(attribute_pb2.RouteDistinguisherIPAddress.DESCRIPTOR):
                        rd = attribute_pb2.RouteDistinguisherIPAddress()
                        labledvpnv4.rd.Unpack(rd)
                        path['rd'] = '{}:{}'.format(rd.admin, rd.assigned)
                    elif labledvpnv4.rd.Is(attribute_pb2.RouteDistinguisherTwoOctetAS.DESCRIPTOR):
                        rd = attribute_pb2.RouteDistinguisherTwoOctetAS()
                        labledvpnv4.rd.Unpack(rd)
                        path['rd'] = '{}:{}'.format(rd.admin, rd.assigned)
                    elif labledvpnv4.rd.Is(attribute_pb2.RouteDistinguisherFourOctetAS.DESCRIPTOR):
                        rd = attribute_pb2.RouteDistinguisherFourOctetAS()
                        labledvpnv4.rd.Unpack(rd)
                        path['rd'] = '{}:{}'.format(rd.admin, rd.assigned)
                    else:
                        # raise or log erron and pass
                        pass
                # todo check if any_pattr in path
                for any_path_attr in _path.pattrs:
                    if any_path_attr.Is(attribute_pb2.OriginAttribute.DESCRIPTOR):
                        origin = attribute_pb2.OriginAttribute()
                        any_path_attr.Unpack(origin)
                        path['origin'] = origin.origin
                    elif any_path_attr.Is(attribute_pb2.AsPathAttribute.DESCRIPTOR):
                        aspath = attribute_pb2.AsPathAttribute()
                        any_path_attr.Unpack(aspath)
                        # todo unpck aspath to segments
                        for segment in aspath.segments:
                            path['aspath'].append(segment.numbers)
                    elif any_path_attr.Is(attribute_pb2.NextHopAttribute.DESCRIPTOR):
                        nexthop = attribute_pb2.NextHopAttribute()
                        any_path_attr.Unpack(nexthop)
                        # path['nexthop'] = nexthop
                    elif any_path_attr.Is(attribute_pb2.ExtendedCommunitiesAttribute.DESCRIPTOR):
                        extcomm = attribute_pb2.ExtendedCommunitiesAttribute()
                        any_path_attr.Unpack(extcomm)
                        for _extcomm in extcomm.communities:
                            if _extcomm.Is(attribute_pb2.TwoOctetAsSpecificExtended.DESCRIPTOR):
                                rt_two_octet_as = attribute_pb2.TwoOctetAsSpecificExtended()
                                _extcomm.Unpack(rt_two_octet_as)
                                path['rt'].append('{}:{}'.format(getattr(rt_two_octet_as, 'as'),
                                                                 rt_two_octet_as.local_admin))
                            elif _extcomm.Is(attribute_pb2.IPv4AddressSpecificExtended.DESCRIPTOR):
                                rt_ipaddr = attribute_pb2.IPv4AddressSpecificExtended()
                                _extcomm.Unpack(rt_ipaddr)
                                path['rt'].append(
                                    '{}:{}'.format(rt_ipaddr.address, rt_ipaddr.local_admin))
                            else:
                                # todo unpack any other extcommunities
                                continue
                    elif any_path_attr.Is(attribute_pb2.MultiExitDiscAttribute.DESCRIPTOR):
                        med = attribute_pb2.MultiExitDiscAttribute()
                        any_path_attr.Unpack(med)
                        # path['med'] = med
                    elif any_path_attr.Is(attribute_pb2.LocalPrefAttribute.DESCRIPTOR):
                        loc_pref = attribute_pb2.LocalPrefAttribute()
                        any_path_attr.Unpack(loc_pref)
                        path['local_pref'] = loc_pref.local_pref
                    elif any_path_attr.Is(attribute_pb2.CommunitiesAttribute.DESCRIPTOR):
                        communities = attribute_pb2.CommunitiesAttribute()
                        any_path_attr.Unpack(communities)
                        path['communities'] = communities.communities
                        # todo convert comm to str
                        # or path['communities'] = communities
                        # for _comm in communities:
                        #    path['communities'].append(_comm)
                    # todo unpack MpReachNLRIAttribute
                table.append(path)
        elif tuple([afi, safi]) == IPV4_UNICAST:
            # todo unpack attribute_pb2.IPAddressPrefix
            pass
        else:
            # todo log.gebug
            raise UnknownAFIError((afi, safi))
        return table

    def get_peers(self, peer_address=''):
        """

        :param peer_address:
        :return:
        """
        peers = {}
        try:
            result = self._stub.ListPeer(gobgp_pb2.ListPeerRequest(address=peer_address))
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise GRPCNetworkError(e)
        for r in result:
            # todo unpack peer params
            peers[r.peer.state.neighbor_address] = {}
            peers[r.peer.state.neighbor_address]['afi_safis'] = []
            for af_saf in r.peer.afi_safis:
                if af_saf.config.enabled:
                    peers[r.peer.state.neighbor_address]['afi_safis'].append((af_saf.config.family.afi,
                                                                              af_saf.config.family.safi))
        return peers

    def get_bgp(self):
        """
        
        :return:
        """
        bgp = {}
        try:
            result = self._stub.GetBgp(gobgp_pb2.GetBgpRequest())
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise GRPCNetworkError(e)
        if result and result.HasField('global'):
            g = getattr(result, 'global')
            bgp['as'] = getattr(g, 'as')
            bgp['router_id'] = getattr(g, 'router_id')
        return bgp
