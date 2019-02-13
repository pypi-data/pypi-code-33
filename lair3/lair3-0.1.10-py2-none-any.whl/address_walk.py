import copy
import re
import socket
import sockets

class SubnetWalker(object):
    def __init__(self, subnet, netmask):
        self.subnet = sockets.resolv_to_dotted(subnet)
        self.netmask = sockets.resolv_to_dotted(netmask)
        self.num_ips = None
        self.curr_ip = None
        self.curr_ip_idx = None
        
        self.reset()
        
    def reset(self):
        self.curr_ip = self.subnet.split('.')
        self.num_ips = (1 << (32 - int(sockets.net2bitmask(self.netmask))))
        self.curr_ip_idx = 0
        
    def next_ip(self):
        if (self.curr_ip_idx >= self.num_ips):
            return None
            
        if (self.curr_ip_idx > 0):
            self.curr_ip[3] = (int(self.curr_ip[3]) + 1) % 256
            if self.curr_ip[3] == 0:
                self.curr_ip[2] = (int(self.curr_ip[2]) + 1) % 256
            if self.curr_ip[2] == 0:
                self.curr_ip[1] = (int(self.curr_ip[1]) + 1) % 256
            if self.curr_ip[1] == 0:
                self.curr_ip[0] = (int(self.curr_ip[0]) + 1) % 256
                
        self.curr_ip_idx += 1
        
        return '.'.join(map(str, self.curr_ip))
            

class IpRange(object):
    def __init__(self, start = None, stop = None, **kwargs):
        self.start = start
        self.stop = stop
        self.options = kwargs
        
    def __eq__(self, other):
        return (other.start == self.start and other.stop == self.stop and other.is_ipv6 == self.is_ipv6 and other.options == self.options)
        
    def __len__(self):
        return (self.stop - self.start + 1)
        
    @property
    def is_ipv6(self):
        return ('ipv6' in self.options and self.options['ipv6'] == True)
        

class IpRangeWalker(object):
    def __init__(self, parse_obj):
        self.curr_range_index = 0
        self.curr_addr = None
        self.length = 0
        
        # copy constructor
        if isinstance(parse_obj, IpRangeWalker) == True:
            self.ranges = copy.copy(parse_obj.ranges)
        else:
            self.ranges = self.parse(parse_obj)
            
        self.reset()

    def __len__(self):
        return self.length
        
    def parse(self, parse_obj):
        if parse_obj is None:
            return None
        ranges = []
        for arg in [y for x in map(lambda a: a.split(' '), parse_obj.split(', ')) for y in x]:
            opts = {}
            
            v4range_mach = re.search(r'^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})-([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$', arg)
            if ":" in arg:
                addrs = arg.split('-', 1)
                
                if len(addrs) == 1:
                    try:
                        addr, scope_id = addrs[0].split('%')
                    except ValueError:
                        addr = addrs[0].split('%')[0]
                        scope_id = None
                        
                    if scope_id is not None:
                        opts['scope_id'] = scope_id
                        
                    opts['ipv6'] = True
                    
                    if sockets.is_ipv6(addr) == False:
                        return False
                    addr = sockets.addr_atoi(addr)
                    ranges.append(IpRange(addr, addr, **opts))
                    continue
                    
                try:
                    addr1, scope_id = addrs[0].split('%')
                except ValueError:
                    addr1 = addrs[0].split('%')[0]
                    scope_id = None
                    
                if scope_id is not None:
                    opts['scope_id'] = scope_id
                    
                try:
                    addr2, scope_id = addrs[0].split('%')
                except ValueError:
                    addr2 = addrs[0].split('%')[0]
                    scope_id = None
                    
                if scope_id is not None and 'scope_id' not in opts:
                    opts['scope_id'] = scope_id
                    
                if sockets.is_ipv6(addr1) == False or sockets.is_ipv6(addr2) == False:
                    return False
                    
                addr1 = sockets.addr_atoi(addr1)
                addr2 = sockets.addr_atoi(addr2)
                
                ranges.append(IpRange(addr1, addr2, **opts))
                continue

            elif '/' in arg:
                if re.search(r'[,-]', arg) is not None:
                    return False
                if len(re.findall("/", arg)) > 1:
                    return False
                
                try:
                    ip_part, mask_part = arg.split("/")
                except ValueError:
                    ip_part = arg.split("/")[0]
                    mask_part = None

                if ip_part is None or len(ip_part) == 0 or mask_part is None or len(mask_part) == 0:
                    return False

                if re.search(r'^[0-9]{1,2}$', mask_part) is None:
                    return False

                if int(mask_part) > 32:
                    return False

                if re.search(r'^\d{1,3}(\.\d{1,3}){1,3}$', ip_part) is not None:
                    if re.search(sockets.MATCH_IPV4, ip_part) is None:
                        return False

                try:
                    sockets.getaddress(ip_part)
                except (socket.gaierror, socket.error) as e:
                    return False

                expanded = self.expand_cidr(arg)
                if expanded is not None and not expanded == False:
                    ranges.append(expanded)
                else:
                    return False

            elif re.search(r'[^-0-9,.*]', arg) is not None:
                try:
                    ranges += map(lambda a: IpRange(a, a, **opts), sockets.resolv_nbo_i_list(arg))
                except (socket.gaierror, socket.error) as e:
                    return False

            elif v4range_mach is not None:
                try:
                    start, stop = sockets.addr_atoi(v4range_mach.group(1)), sockets.addr_atoi(v4range_mach.group(2))
                    if start > stop:
                        return False
                    ranges.append(IpRange(start, stop, **opts))
                except (socket.gaierror, socket.error) as e:
                    return False

            else:
                expanded = self.expand_nmap(arg)
                if expanded:
                    for r in expanded:
                        ranges.append(r)

        def list_uniq(duplicate): 
            final_list = [] 
            for num in duplicate: 
                if num not in final_list: 
                    final_list.append(num) 
            return final_list 

        ranges = list_uniq(ranges)
        return ranges
            
    def reset(self):
        if self.valid == False:
            return False
        self.curr_range_index = 0
        self.curr_addr = self.ranges[0].start
        self.length = 0
        for r in self.ranges:
            self.length += len(r)

        return self
    
    def next_ip(self):
        if not self.valid:
            return False

        if (self.curr_addr > self.ranges[self.curr_range_index].stop):
            try:
                if self.ranges[self.curr_range_index + 1] is None:
                    return False
            except IndexError:
                return False

            self.curr_range_index += 1

            self.curr_addr = self.ranges[self.curr_range_index].start
        addr = sockets.addr_itoa(self.curr_addr, self.ranges[self.curr_range_index].is_ipv6)

        if 'scope_id' in self.ranges[self.curr_range_index].options:
            addr = addr + '%' + self.ranges[self.curr_range_index].options['scope_id']

        self.curr_addr += 1
        return addr

    @property
    def valid(self):
        return ((self.ranges is not None or not self.ranges == False) and (len(self.ranges) != 0))
                    
    def expand_cidr(self, arg):
        try:
            start, stop = sockets.cidr_crack(arg)
        except ValueError:
            return False
            
        return IpRange(sockets.addr_atoi(start), sockets.addr_atoi(stop), ipv6 = (':' in arg))
        
    def expand_nmap(self, arg):
        if ':' in arg:
            return False
            
        if ',-' in arg or '-,' in arg:
            return False
            
        bytes = []
        sections = arg.split('.')
        if len(sections) != 4:
            return False
            
        for section in sections:
            if len(section) == 0:
                section = "0"
                
            if section == "*":
                section = "0-255"
            elif '*' in section:
                return False

            ranges = section.split(',', -1)
            sets = []
            for r in ranges:
                bounds = []
                if '-' in r:
                    bounds = r.split('-', -1)
                    if len(bounds) > 2:
                        return False
                
                    if bounds[0] is None or len(bounds[0]) == 0:
                        bounds[0] = 0
                        
                    if bounds[1] is None or len(bounds[0]) == 0:
                        bounds[1] = 255

                    bounds = map(lambda b: int(b), bounds)
                    if (bounds[0] > bounds[1]):
                        return False
                else:
                    bounds.insert(0, int(r))
                if bounds[0] > 255 or (len(bounds) > 1 and bounds[1] > 255):
                    return False
                if len(bounds) > 1 and (bounds[0] > bounds[1]):
                    return False
                if len(bounds) > 1:
                    for i in range(bounds[0], bounds[1] + 1):
                        sets.append(i)
                elif len(bounds) == 1:
                    sets.append(bounds[0])
            bytes.append(sorted(set(sets)))

        addrs = []
        for a in bytes[0]:
            for b in bytes[1]:
                for c in bytes[2]:
                    for d in bytes[3]:
                        ip = (a << 24) + (b << 16) + (c << 8) + d
                        addrs.append(ip)

        addrs = sorted(set(addrs))
        rng = IpRange()
        rng.options = {'ipv6':False}
        rng.start = addrs[0]

        ranges = []
        for idx in range(1, len(addrs)):
            if addrs[idx - 1] + 1 == addrs[idx]:
                continue
            else:
                rng.stop = addrs[idx - 1]
                ranges.append(copy.copy(rng))
                rng.start = addrs[idx]
        rng.stop = addrs[len(addrs) - 1]
        ranges.append(copy.copy(rng))
        return ranges
            
                
                