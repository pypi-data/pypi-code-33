"""MHL class file."""

import netaddr
import re

from bits.mhl.types import AvailableIp, CnameRecord, Comment, \
    Host, MxRecord, NsRecord, ReservedIp

# define the field names of the mhl columns in order
FIELDNAMES = [
    'target',       # IP or CNAME/MX/NS Target
    'username',     # Username (Owner)
    'mac',          # MAC Address (or MX Priority)
    'hostnames',    # Hostnames (comma-separated)
    'ttl',          # TTL
    'hosttype',     # Host Type
    'location',     # Location code (see LOCATIONS below)
    'tags',         # Tags for runaround, icinga, etc.
    'comments',     # Comments
]

# define a list of valid host types
HOSTTYPES = [
    'chrome',       # Chrome OS Desktop or Laptop
    'cname',        # Special type for DNS CNAME records
    'device',       # Generic host without DHCP
    'dhcpdevice',   # Generic host with DHCP
    'external',     # External (non-Broad) host (Amazon, Google, etc.)
    'ip_alias',     # Additional IP Alias on Host (same MAC as host)
    'mac_svr',      # Mac OS X Server
    'mac',          # Mac OS X Desktop or Laptop
    'mx',           # Special type for DNS MX records
    'netapp',       # NetApp Filers
    'ns',           # Special type for DNS NS records
    'pc',           # Windows or Linux Desktop or Laptop
    'printer',      # Printer
    'round_robin',  # Special type to handle hosts with Round Robin DNS
    'unix_svr',     # Unix Server
    'win_svr',      # Windows Desktop or Laptop
]

# define a list of valid locations
LOCATIONS = [
    'a',  # 75 Ames Street
    'b',  # 105 Broadway
    'c',  # 320 Charles Street
    'e',  # 190 Fifth Street (decommissioned)
    'g',  # 415 Main Street / 7 Cambridge Center
    'i',  # 50 Inner Belt
    'l',  # LIMS Network
    'r',  # Remote site (ex. Oxford Street)
    's',  # 1 Summer Street
    'v',  # 5 Cambridge Center (decommissioned)
    'w',  # Broad Internal Wifi
    'x',  # Museum
]

# define a list of non-people owners of hosts
SPECIAL_OWNERS = [
    'BITS Computer',
    'Classroom Computer',
    'Conference Room Computer',
    'Hotel Computer',
    'Loaner Computer',
]

#
# Network Ranges
#

# define the broad network ip ranges
BROAD_HOSTS = netaddr.IPSet([
    # loopback
    netaddr.IPNetwork('127.0.0.1/32'),

    # internal ranges
    netaddr.IPNetwork('10/8'),
    netaddr.IPNetwork('172.16/12'),
    netaddr.IPNetwork('192.168.0.0/16'),

    # public range
    netaddr.IPNetwork('69.173.64.0/18'),

    # networking points
    netaddr.IPAddress('207.210.142.158'),   # nox cps interface
    netaddr.IPAddress('207.210.143.158'),   # nox r&e interface
    netaddr.IPAddress('216.55.4.6'),        # xo interface
    netaddr.IPAddress('4.53.50.78'),        # level 3 interface
])

# regular hosts
REGULAR_HOSTS = netaddr.IPSet([
    netaddr.IPNetwork('10.1/20'),
    netaddr.IPNetwork('10.1.128/24'),
    netaddr.IPNetwork('10.75.0/20'),
    netaddr.IPNetwork('10.75.100/22'),
    netaddr.IPNetwork('10.75.104/22'),
    netaddr.IPNetwork('10.75.108/22'),
    netaddr.IPNetwork('10.75.112/22'),
    netaddr.IPNetwork('10.75.116/24'),
    netaddr.IPNetwork('10.75.16/21'),
    netaddr.IPNetwork('172.18.12/24'),
    netaddr.IPNetwork('18.103.12/22'),
    netaddr.IPNetwork('18.103.16/21'),
    netaddr.IPNetwork('18.103.2/23'),
    netaddr.IPNetwork('18.103.24/22'),
    netaddr.IPNetwork('69.173.104/22'),
    netaddr.IPNetwork('69.173.108/22'),
    netaddr.IPNetwork('69.173.114/24'),
    netaddr.IPNetwork('69.173.115/24'),
    netaddr.IPNetwork('69.173.120/22'),
    netaddr.IPNetwork('69.173.96/21'),
])
REGULAR_HOSTS.add(netaddr.IPRange('192.168.141.150', '192.168.141.255'))

# cellario network hosts
CELLARIO_HOSTS = netaddr.IPNetwork('192.168.10/23')

# lab network hosts
LAB_HOSTS = netaddr.IPSet([
    netaddr.IPNetwork('192.168.1/24'),
    netaddr.IPNetwork('192.168.2/23'),
    netaddr.IPNetwork('192.168.8/23'),
    netaddr.IPNetwork('192.168.96/21'),

    netaddr.IPNetwork('192.168.212/24'),
])
LAB_HOSTS.add(netaddr.IPRange('192.168.141.0', '192.168.141.150'))
LAB_HOSTS.add(netaddr.IPRange('192.168.200.20', '192.168.200.127'))

# qa network hosts
QA_HOSTS = netaddr.IPNetwork('192.168.105/24')

# restricted network hosts
RESTRICTED_HOSTS = netaddr.IPNetwork('192.168.60/24')


class MHL(object):
    """MHL class."""

    def __init__(
        self,
        path='/sysman/install/broad/master.host.listing',
        lockfile='/sysman/install/broad/locks/master.host.listing.lock',
        people=None,
        verbose=False
    ):
        """Initialize the object."""
        self.path = path
        self.lockfile = lockfile
        self.verbose = verbose
        self.mhlfile = MHLFile(self, path, lockfile, people, verbose=self.verbose)


class MHLFile(object):
    """MHL class."""

    def __init__(self, mhl, path, lockfile, people, verbose=False):
        """Initialize the object."""
        self.mhl = mhl
        self.path = path
        self.people = people
        self.lockfile = lockfile
        self.verbose = verbose

        # get the lines of the mhl as objects
        self.lines = self.get_lines()
        self.linecount = len(self.lines)

        # records
        self.cnames = {}
        self.hosts = {}
        self.mxs = {}
        self.nss = {}
        self.records = {}

        # tracking duplicates
        self.hostnames = {}
        self.ips = {}
        self.macs = {}

        # get records
        self.get_records()

        # round robins
        self.round_robins = self.get_round_robins()

        # statistics
        self.hosttypes = self.get_hosttypes()
        self.kinds = self.get_kinds()
        self.record_types = self.get_record_types()
        self.types = self.get_types()

        # check for errors, warnings, duplicates and out-of-order issues
        self.check_lines()
        self.check_duplicates()
        self.check_order()

        # if we have people data, let's add emplids to all our host records
        self.insert_emplids(people)

        # errors and warnings
        self.errors = self.get_errors()
        self.warnings = self.get_warnings()

        # find missing IP addresses
        self.missing_ips = self.get_missing_ips()

    def check_duplicate_available_ips(self):
        """Check available IPs for duplicates."""
        for line in self.lines:
            if line.kind != 'available_ip':
                continue
            entry = line.entry
            ip = entry.ip
            if ip not in self.ips:
                self.ips[ip] = line
            else:
                warning = 'Duplicate Available IP Address: %s' % (ip)
                line.warnings.append(warning)

    def check_duplicate_hosts(self, kind='entry'):
        """Check host entries for duplicates."""
        # now check host lines for duplicates
        for line in self.lines:
            if line.kind != kind:
                continue

            entry = line.entry
            hostname = entry.hostname

            # only look at host entries
            if entry.type != 'host':
                continue

            # check hostname
            if hostname not in self.hostnames:
                self.hostnames[hostname] = line
            else:
                error = 'Duplicate Hostname: %s' % (hostname)
                line.errors.append(error)

            # check cnames
            cnames = entry.cnames
            for cname in cnames:
                if cname not in self.hostnames:
                    self.hostnames[cname] = line
                else:
                    error = 'Duplicate Hostname: %s' % (cname)
                    line.errors.append(error)

            # check ip address
            ip = entry.ip
            if ip and ip != '-':
                if ip not in self.ips:
                    self.ips[ip] = line
                else:
                    error = 'Duplicate IP Address: %s' % (ip)
                    line.errors.append(error)

            # check mac address
            if entry.hosttype not in ['ip_alias']:
                mac = entry.mac
                if mac and mac != '-':
                    if mac not in self.macs:
                        self.macs[mac] = line
                    else:
                        error = 'Duplicate MAC Address: %s' % (mac)
                        line.errors.append(error)

    def check_duplicate_reserved_ips(self):
        """Check reserved IPs for duplicates."""
        for line in self.lines:
            if line.kind != 'reserved_ip':
                continue
            entry = line.entry
            ip = entry.ip
            if ip not in self.ips:
                self.ips[ip] = line
            else:
                warning = 'Duplicate Reserved IP Address: %s' % (ip)
                line.warnings.append(warning)

    def check_duplicates(self):
        """Check entries for duplicates."""
        # add round robins first
        for hostname in self.round_robins:
            self.hostnames[hostname] = self.round_robins[hostname]

        # add cnames, mx records and ns record next
        for hostname in self.cnames:
            self.hostnames[hostname] = self.cnames[hostname]
        for hostname in self.mxs:
            self.hostnames[hostname] = self.mxs[hostname]
        for hostname in self.nss:
            self.hostnames[hostname] = self.nss[hostname]

        # check reserved IPs for duplicates
        self.check_duplicate_reserved_ips()

        # check host records for duplicates
        self.check_duplicate_hosts()

        # check disabled host records for duplicates
        self.check_duplicate_hosts(kind='disabled_entry')

        # check available IPs
        self.check_duplicate_available_ips()

    def check_lines(self):
        """Check the lines of the MHL files."""
        for line in self.lines:
            if not line or not line.entry:
                continue
            line.entry.check()

    def get_missing_ips(self):
        """Check the file for missing IP addresses."""
        missing_ips = []
        subnets = {}
        for line in self.lines:
            if not line.entry:
                continue
            if not line.entry.ip:
                continue
            subnet = '.'.join(line.entry.ip.split('.')[:3])
            cidr = netaddr.IPNetwork('%s.0/24' % (subnet))
            if cidr not in subnets:
                subnets[cidr] = []
            subnets[cidr].append(netaddr.IPAddress(line.entry.ip))

        # check each subnet for missing ips
        for subnet in sorted(subnets):
            ips = sorted(subnets[subnet])

            # get the start and end ips from mhl
            first = ips[0]
            last = ips[-1]
            iprange = netaddr.IPSet(netaddr.IPRange(first, last))

            # get the used ips from the file
            usedips = netaddr.IPSet(ips)

            # find the ips that are missing from the file
            missing = iprange ^ usedips

            if not missing:
                continue

            missing_ips.extend(missing)

            # display missiong IP addresses
            if self.verbose:
                print('%s missing IPs: %s' % (
                    subnet,
                    len(missing),
                ))

        return sorted(missing_ips)

    def display_errors(self):
        """Display errors."""
        errors = self.get_errors()
        if errors:
            print('\nERRORS [%s]:' % (len(errors)))
            for line in errors:
                print('\n%s: %s' % (line.linenum, line.line))
                print('  - '+'\n  - '.join(line.errors))

    def display_warnings(self):
        """Display warnings."""
        warnings = self.get_warnings()
        if warnings:
            print('\nWarnings [%s]:' % (len(warnings)))
            for line in warnings:
                print('\n%s: %s' % (line.linenum, line.line))
                print('  - '+'\n  - '.join(line.warnings))

    def get_errors(self):
        """Return a list of lines with errors."""
        errors = []
        for line in self.lines:
            if line.errors:
                errors.append(line)
        self.errors = errors
        return errors

    def get_hosttypes(self):
        """Return a dict of the entry hosttypes in the file."""
        hosttypes = {}
        for line in self.lines:
            if line.entry and line.entry.type == 'host':
                hosttype = line.entry.hosttype
                if hosttype in hosttypes:
                    hosttypes[hosttype] += 1
                else:
                    hosttypes[hosttype] = 1
        return hosttypes

    def get_kinds(self):
        """Return a dict of the kinds in the file."""
        kinds = {}
        for line in self.lines:
            if line.kind not in kinds:
                kinds[line.kind] = 1
            else:
                kinds[line.kind] += 1
        return kinds

    def get_lines(self):
        """Get the lines of the MHL in object form."""
        lines = []
        linenum = 0
        for line in self.readlines():
            linenum += 1
            o = MHLLine(line, linenum, self.verbose)
            lines.append(o)
        return lines

    def check_order(self):
        """Check order of IP addresses in the file."""
        # check for out of order IP addresses in the file
        last_ip = None

        for line in self.lines:
            # skip empty lines
            if not line:
                continue

            # skip non-entries or entries without an ip:
            if not line.entry or not line.entry.ip:
                continue

            # skip entries with an invalid ip address
            try:
                ip = netaddr.IPAddress(line.entry.ip)
            except Exception as e:
                print('%s\n\t%s' % (line.line, e))
                continue

            # check the order of the ip addresses in the file
            if not last_ip:
                last_ip = ip
            else:
                if last_ip > ip:
                    error = 'IP Address out of order: %s' % (line.entry.ip)
                    line.errors.append(error)
                last_ip = ip

    def get_records(self):
        """Assemble all lines into records."""
        # for each line that is an entry, determine what type it is
        # for mx and ns records, collapse same-named records into one record
        # with multiple targets
        for line in self.lines:
            if line.kind != 'entry':
                continue

            entry = line.entry
            hostname = entry.hostname
            # cname
            if entry.type == 'cname':
                if hostname not in self.cnames:
                    self.cnames[hostname] = entry
                else:
                    error = 'Duplicate CNAME: %s' % (hostname)
                    line.errors.append(error)
            # mx
            elif entry.type == 'mx':
                if hostname not in self.mxs:
                    self.mxs[hostname] = entry
                else:
                    self.mxs[hostname].targets += entry.targets
            # ns
            elif entry.type == 'ns':
                if hostname not in self.nss:
                    self.nss[hostname] = entry
                else:
                    self.nss[hostname].targets += entry.targets
            # host
            elif entry.type == 'host':
                if hostname not in self.hosts:
                    self.hosts[hostname] = entry
                else:
                    error = 'Duplicate Host: %s' % (hostname)
                    line.errors.append(error)

        # now that we've turned the entries into records, check for duplicates

        # cnames
        for hostname in self.cnames:
            if hostname not in self.records:
                self.records[hostname] = self.cnames[hostname]
            else:
                error = 'Duplicate Record [CNAME]: %s' % (hostname)
                line.errors.append(error)

        # mx records
        for hostname in self.mxs:
            if hostname not in self.records:
                self.records[hostname] = self.mxs[hostname]
            else:
                error = 'Duplicate Record [MX]: %s' % (hostname)
                line.errors.append(error)

        # ns records
        for hostname in self.nss:
            if hostname not in self.records:
                self.records[hostname] = self.nss[hostname]
            else:
                error = 'Duplicate Record [NS]: %s' % (hostname)
                line.errors.append(error)

        # hosts
        for hostname in self.hosts:
            if hostname not in self.records:
                self.records[hostname] = self.hosts[hostname]
            else:
                error = 'Duplicate Record [Host]: %s' % (hostname)
                line.errors.append(error)

    def get_record_types(self):
        """Return a dict of the record types in the file."""
        record_types = {}
        for hostname in self.records:
            record = self.records[hostname]
            record_type = record.type
            if record_type in record_types:
                record_types[record_type] += 1
            else:
                record_types[record_type] = 1
        return record_types

    def get_round_robins(self):
        """Get round robin hosts."""
        round_robins = {}
        for hostname in self.hosts:
            host = self.hosts[hostname]
            if host.round_robin:
                round_robin = host.round_robin
                if round_robin in round_robins:
                    round_robins[round_robin].append(host)
                else:
                    round_robins[round_robin] = [host]
        return round_robins

    def get_types(self):
        """Return a dict of the entry types in the file."""
        types = {}
        for line in self.lines:
            if line.entry:
                hosttype = line.entry.type
                if hosttype in types:
                    types[hosttype] += 1
                else:
                    types[hosttype] = 1
        return types

    def get_warnings(self):
        """Return a list of lines with warnings."""
        warnings = []
        for line in self.lines:
            if line.warnings:
                warnings.append(line)
        self.warnings = warnings
        return warnings

    def insert_emplids(self, people):
        """Insert emplids into all Host records that have owners."""
        if not people:
            return
        # create username -> emplid map
        emplids = {}
        for username in people:
            emplids[username] = people[username]['emplid']
        # update all hosts
        for hostname in self.hosts:
            host = self.hosts[hostname]
            username = host.username.replace('-', '')
            if not username:
                continue
            if username in people:
                host.owner.emplid = emplids[username]

    def readlines(self):
        """Read in the lines of the MHL file."""
        mhlfile = open(self.path, 'r')
        return mhlfile.readlines()

    def update_file(self):
        """Update the production instance of the MHL file."""
        # RCS version
        # - if lockfile already exists, exit
        # - create a lockfile
        # - checkout the mhl file from RCS
        # - verify that file is now checked out by me and locked
        # - write out a new copy of the file to a temporary location
        # - compare the two files and provide a diff
        # - overwrite the real file with the new file
        # - verify the two files are now the same
        # - check the file into RCS
        # - verify the file has been checked into RCS
        # return success

        # GCS version
        # write file to a GCS bucket - magic happens

        # GIT version
        # clone a version of the mhl repo into a directory
        # replace the mhl with the new version
        # check the git diff
        # git commit the changes
        # git push the changes

    def writelines(self, filename):
        """Write out the MHL file to disk."""
        # write out a new copy of the mhl to disk
        outputfile = open(filename, 'w')
        lines = []
        for line in self.lines:
            lines.append('%s\n' % (line.line))
        outputfile.writelines(lines)

    def writemissing(self, filename):
        """Write out the MHL file to disk including missing IPs."""
        # write out a new copy of the mhl to disk
        outputfile = open(filename, 'w')
        lines = []

        missing_ips = sorted(self.missing_ips)

        last_ip = None

        for line in self.lines:
            ip = None
            if line.entry and line.entry.ip:
                ip = netaddr.IPAddress(line.entry.ip)

            if not last_ip:
                last_ip = ip

            while ip and missing_ips and ip > missing_ips[0]:
                lines.append('#%s\n' % (missing_ips.pop(0)))

            lines.append('%s\n' % (line.line))
        outputfile.writelines(lines)


class MHLLine(object):
    """MHL Line class."""

    fieldnames = FIELDNAMES
    hosttypes = HOSTTYPES
    locations = LOCATIONS
    special_owners = SPECIAL_OWNERS

    # network ranges
    broad_hosts = BROAD_HOSTS
    cellario_hosts = CELLARIO_HOSTS
    lab_hosts = LAB_HOSTS
    qa_hosts = QA_HOSTS
    regular_hosts = REGULAR_HOSTS
    restricted_hosts = RESTRICTED_HOSTS

    def __init__(self, line, linenum, verbose=False):
        """Initialize the object."""
        self.line = line.strip()
        self.linenum = linenum
        self.fields = line.strip().split('|')

        # errors and warnings
        self.errors = []
        self.warnings = []

        # blanks and comments
        self.is_blank = False
        self.is_comment = False

        # check if line is blank
        if not line.strip():
            self.is_blank = True
        # check if line is a comment
        elif re.match('^#', line):
            self.is_comment = True

        # set kind
        self.kind = self.get_kind()

        # set entry
        self.entry = self.get_entry()

    def check_ip(self, ip):
        """Check an IP address for validity."""
        errors = []
        try:
            netaddr.IPAddress(ip)
            # check if this ip address is in one of our known ranges
            if ip not in self.broad_hosts:
                error = 'Unknown Network: %s' % (ip)
                self.warnings.append(error)
        except netaddr.core.AddrFormatError:
            error = 'Invalid IP Address: %s' % (ip)
            errors.append(error)
        return errors

    def get_entry(self):
        """Return an entry based on the current line."""
        # blank entries
        if self.kind == 'blank':
            return None

        # errors
        if self.kind == 'error':
            error = 'Incorrect Field Count: %s' % (len(self.fields))
            self.errors.append(error)
            return None

        # comments
        elif self.is_comment:
            if self.kind == 'available_ip':
                return AvailableIp(self)
            if self.kind == 'disabled_entry':
                hosttype = self.to_json().get('hosttype')
                if hosttype == 'cname':
                    return CnameRecord(self, disabled=True)
                elif hosttype == 'mx':
                    return MxRecord(self, disabled=True)
                elif hosttype == 'ns':
                    return NsRecord(self, disabled=True)
                return Host(self, disabled=True)
            if self.kind == 'reserved_ip':
                return ReservedIp(self)
            return Comment(self)

        # entries
        elif self.kind == 'entry':
            hosttype = self.to_json().get('hosttype')
            if hosttype == 'cname':
                return CnameRecord(self)
            elif hosttype == 'mx':
                return MxRecord(self)
            elif hosttype == 'ns':
                return NsRecord(self)
            return Host(self)

    def get_kind(self):
        """Return the kind of the current line."""
        # blank line
        if self.is_blank:
            return 'blank'

        # comments, disabled entries and reserved IPs
        if self.is_comment:
            if len(self.fields) == len(self.fieldnames):
                return 'disabled_entry'
            elif len(self.fields) == 2:
                return 'reserved_ip'
            elif re.match(r'^#([0-9]+)(\.[0-9]+){3}', self.line):
                return 'available_ip'
            return 'comment'

        # entries
        if len(self.fields) == len(self.fieldnames):
            return 'entry'

        return 'error'

    def to_json(self):
        """Return a json representation of an MHL line."""
        line = {}
        fields = list(self.fields)
        for key in self.fieldnames:
            if fields:
                line[key] = fields.pop(0)
        return line
