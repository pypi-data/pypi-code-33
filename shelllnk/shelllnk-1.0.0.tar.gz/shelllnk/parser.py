import enum
import datetime


HEADER_SIZE = 0x4C
LINK_CLSID = b"\x01\x14\x02\x00" \
             b"\x00\x00" \
             b"\x00\x00" \
             b"\xC0\x00"\
             b"\x00\x00\x00\x00\x00\x46"


class LinkFlags(enum.IntFlag):
    has_target_id_list = 0x0001
    has_link_info = 0x0002
    has_name = 0x0004
    has_relative_path = 0x0008
    has_working_dir = 0x0010
    has_arguments = 0x0020
    has_icon_location = 0x0040
    is_unicode = 0x0080
    force_no_link_info = 0x0100
    has_exp_string = 0x0200
    run_in_separate_process = 0x0400
    has_darwin_id = 0x1000
    run_as_user = 0x2000
    has_exp_icon = 0x4000
    no_pidl_aliasa = 0x8000
    run_with_shim_layer = 0x20000
    force_no_link_track = 0x40000
    enable_target_metadata = 0x80000
    disable_link_path_tracking = 0x100000
    disable_known_folder_tracking = 0x200000
    disable_known_folder_alias = 0x400000
    allow_link_to_link = 0x800000
    unalias_on_save = 0x1000000
    prefer_environment_path = 0x2000000
    keep_local_id_list_for_unc_target = 0x4000000


class FileAttributeFlags(enum.IntFlag):
    file_attribute_read_only = 0x0001
    file_attribute_hidden = 0x0002
    file_attribute_system = 0x0004
    file_attribute_directory = 0x0010
    file_attribute_archive = 0x0020
    file_attribute_normal = 0x0080
    file_attribute_temporary = 0x0100
    file_attribute_sparse_file = 0x0200
    file_attribute_reparse_point = 0x0400
    file_attribute_compressed = 0x0800
    file_attribute_offline = 0x1000
    file_attribute_not_content_indexed = 0x2000
    file_attribute_encrypted = 0x4000


class LinkInfoFlags(enum.IntFlag):
    volume_id_and_local_base_path = 0x0001
    common_network_relative_link_and_path_suffix = 0x0002


class DriveType(enum.IntEnum):
    drive_unknown = 0x0000
    drive_no_root_dir = 0x0001
    drive_removable = 0x0002
    drive_fixed = 0x0003
    drive_remote = 0x0004
    drive_cdrom = 0x0005
    drive_ramdisk = 0x0006


class NetworkProviderType(enum.IntEnum):
    WNNC_NET_MSNET = 0x00010000
    WNNC_NET_LANMAN = 0x00020000
    WNNC_NET_NETWARE = 0x00030000
    WNNC_NET_VINES = 0x00040000
    WNNC_NET_10NET = 0x00050000
    WNNC_NET_LOCUS = 0x00060000
    WNNC_NET_SUN_PC_NFS = 0x00070000
    WNNC_NET_LANSTEP = 0x00080000
    WNNC_NET_9TILES = 0x00090000
    WNNC_NET_LANTASTIC = 0x000A0000
    WNNC_NET_AS400 = 0x000B0000
    WNNC_NET_FTP_NFS = 0x000C0000
    WNNC_NET_PATHWORKS = 0x000D0000
    WNNC_NET_LIFENET = 0x000E0000
    WNNC_NET_POWERLAN = 0x000F0000
    WNNC_NET_BWNFS = 0x00100000
    WNNC_NET_COGENT = 0x00110000
    WNNC_NET_FARALLON = 0x00120000
    WNNC_NET_APPLETALK = 0x00130000
    WNNC_NET_INTERGRAPH = 0x00140000
    WNNC_NET_SYMFONET = 0x00150000
    WNNC_NET_CLEARCASE = 0x00160000
    WNNC_NET_FRONTIER = 0x00170000
    WNNC_NET_BMC = 0x00180000
    WNNC_NET_DCE = 0x00190000
    WNNC_NET_AVID =  0x001A0000
    WNNC_NET_DOCUSPACE = 0x001B0000
    WNNC_NET_MANGOSOFT = 0x001C0000
    WNNC_NET_SERNET = 0x001D0000
    WNNC_NET_RIVERFRONT1 = 0X001E0000
    WNNC_NET_RIVERFRONT2 = 0x001F0000
    WNNC_NET_DECORB = 0x00200000
    WNNC_NET_PROTSTOR = 0x00210000
    WNNC_NET_FJ_REDIR = 0x00220000
    WNNC_NET_DISTINCT = 0x00230000
    WNNC_NET_TWINS = 0x00240000
    WNNC_NET_RDR2SAMPLE = 0x00250000
    WNNC_NET_CSC = 0x00260000
    WNNC_NET_3IN1 = 0x00270000
    WNNC_NET_EXTENDNET = 0x00290000
    WNNC_NET_STAC  = 0x002A0000
    WNNC_NET_FOXBAT = 0x002B0000
    WNNC_NET_YAHOO = 0x002C0000
    WNNC_NET_EXIFS = 0x002D0000
    WNNC_NET_DAV = 0x002E0000
    WNNC_NET_KNOWARE = 0x002F0000
    WNNC_NET_OBJECT_DIRE = 0x00300000
    WNNC_NET_MASFAX = 0x00310000
    WNNC_NET_HOB_NFS = 0x00320000
    WNNC_NET_SHIVA = 0x00330000
    WNNC_NET_IBMAL = 0x00340000
    WNNC_NET_LOCK = 0x00350000
    WNNC_NET_TERMSRV = 0x00360000
    WNNC_NET_SRT = 0x00370000
    WNNC_NET_QUINCY = 0x00380000
    WNNC_NET_OPENAFS = 0x00390000
    WNNC_NET_AVID1 = 0X003A0000
    WNNC_NET_DFS = 0x003B0000
    WNNC_NET_KWNP = 0x003C0000
    WNNC_NET_ZENWORKS = 0x003D0000
    WNNC_NET_DRIVEONWEB = 0x003E0000
    WNNC_NET_VMWARE = 0x003F0000
    WNNC_NET_RSFX = 0x00400000
    WNNC_NET_MFILES = 0x00410000
    WNNC_NET_MS_NFS = 0x00420000
    WNNC_NET_GOOGLE = 0x00430000


class CommonNetworkRelativeLinkFlags(enum.IntFlag):
    valid_device = 0x1
    valid_net_type = 0x2


def readu32(fd, loc=None):
    """
    Read an unsigned 32-bit number
    :param fd: file handle
    :param loc: seek location
    :return: a 4-byte number
    """
    if loc is not None:
        fd.seek(loc)
    data = fd.read(4)
    return data[0] + 256 *(data[1] + 256 *(data[2] + 256 * data[3]))


def readu16(fd, loc=None):
    """
    Read an unsigned 16-bit number
    :param fd: file handle
    :param loc: seek location
    :return: a 4-byte number
    """
    if loc is not None:
        fd.seek(loc)
    data = fd.read(4)
    return data[0] + 256 *data[1]


def read_datetime(fd, loc=None):
    """
    Read a datetime

    :param fd: file handle
    :param loc: seek location
    :return: a datetime.datetime of the parsed date
    """
    if loc is None:
        hiloc = None
    else:
        hiloc = loc + 4
    time_100_ns = readu32(fd, loc) + (2 **32) * readu32(fd, hiloc)
    time_sec = time_100_ns / 1000. / 1000 / 10
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(0, time_sec)


def read_string(fd, loc=None):
    """
    Read a null-terminated string.
    The file descriptor is set to one past the null.

    :param fd: file handle opened in binary mode
    :return: the decoded string
    """
    if loc is not None:
        fd.seek(loc)
    b = b""
    while True:
        bb = fd.read(1)
        if bb == b"\x00":
            break
        b += bb
    return b.decode("utf-8")


def read_string_data(fd, loc=None):
    """
    This is a 16-bit length + following string

    :param fd: file descriptor
    :param loc: optional file offset
    :return: decoded string
    """
    if loc is not None:
        fd.seek(loc)
    length = readu16(fd, loc)
    return fd.read(length).decode("utf-8")


class ShellLnk:

    @staticmethod
    def parse(fd):
        """
        Parse a .lnk file
        :param fd: file handle
        :return: a ShellLnk datastructure
        """
        result = ShellLnk()
        result.do_parse(fd)
        return result

    def do_parse(self, fd):
        """
        Do the parsing

        :param fd: a file descriptor
        """
        # Shell link header
        #
        # 0-3    Header size
        # 4-19   Link Class ID
        # 20-23  Link Flags
        # 24-27  File attributes
        # 28-35  Creation time
        # 36-43  Access time
        # 44-51  Write time
        # 52-55  File size
        # 56-59  Icon index
        # 60-63  Show command
        # 64-65  Hot key
        # 66-85  Reserved

        header_size = readu32(fd)
        if header_size != HEADER_SIZE:
            raise ValueError("Header size was %d, expected %d" %
                             (header_size, HEADER_SIZE))
        clsid = fd.read(16)
        if clsid != LINK_CLSID:
            raise ValueError("Invalid class ID in header, not a .LNK file")
        self.link_flags = readu32(fd)
        self.file_attributes = readu32(fd)
        self.creation_time = read_datetime(fd)
        self.access_time = read_datetime(fd)
        self.write_time = read_datetime(fd)
        self.file_size = readu32(fd)
        self.icon_index = readu32(fd)
        self.show_command = readu32(fd)
        self.hot_key = readu16(fd)
        #
        # The item ID list
        #
        if self.link_flags & LinkFlags.has_target_id_list:
            id_list_size = readu16(fd)
            self.item_id_list = []
            for i in range(id_list_size):
                item_size = readu16(fd)
                self.item_id_list.append(fd.read(item_size))
        else:
            self.item_id_list = None
        fd.seek(header_size)
        #
        # The link info list
        #
        if self.link_flags & LinkFlags.has_link_info:
            link_info_start = header_size
            link_info_size = readu32(fd)
            link_info_end = header_size + link_info_size
            link_info_header_size = readu32(fd)
            self.link_info_flags = readu32(fd)
            volume_id_offset = readu32(fd)
            local_base_path_offset = readu32(fd)
            common_network_relative_link_offset = readu32(fd)
            common_path_suffix_offset = readu32(fd)
            if link_info_header_size >= 0x24:
                local_base_path_offset = readu32(fd)
                common_path_suffix_offset = readu32(fd)
            if self.link_info_flags & LinkInfoFlags.volume_id_and_local_base_path:
                fd.seek(link_info_start + volume_id_offset)
                volume_id_size = readu32(fd)
                self.drive_type = readu32(fd)
                self.drive_serial_number = readu32(fd)
                volume_label_offset = readu32(fd)
                if volume_label_offset > 0x14:
                    self.volume_label = read_string(
                        fd, link_info_start + volume_label_offset)
                else:
                    volume_label_offset_unicode = readu32(fd)
                    self.volume_label = read_string(
                        fd, link_info_start + volume_label_offset_unicode)
                self.local_base_path = read_string(
                    fd, link_info_start + local_base_path_offset)
            if self.link_info_flags & LinkInfoFlags.common_network_relative_link_and_path_suffix:
                common_nrl_start = header_size + common_network_relative_link_offset
                nrl_size = readu32(fd)
                self.common_nrl_link_flags = readu32(fd)
                net_name_offset = readu32(fd)
                device_name_offset = readu32(fd)
                self.network_provider_type = readu32(fd)
                if net_name_offset > 0x14:
                    net_name_offset = readu32(fd)
                    device_name_offset = readu32(fd)
                self.net_name = read_string(fd, common_nrl_start + net_name_offset)
                if self.common_nrl_link_flags & CommonNetworkRelativeLinkFlags.valid_device:
                    self.device_name = read_string(fd, common_nrl_start + device_name_offset)
                else:
                    self.device_name = ""
            self.common_base_path_suffix = read_string(fd, link_info_start + common_path_suffix_offset)
            fd.seek(link_info_end)
        if self.link_flags & LinkFlags.has_name:
            self.name = read_string_data(fd)
        if self.link_flags & LinkFlags.has_relative_path:
            self.relative_path = read_string_data(fd)
        if self.link_flags & LinkFlags.has_working_dir:
            self.working_dir = read_string_data(fd)
        if self.link_flags & LinkFlags.has_arguments:
            self.command_line_arguments = read_string_data(fd)
        if self.link_flags & LinkFlags.has_icon_location:
            self.icon_location = read_string_data(fd)
        while True:
            loc = fd.tell()
            length = readu32(fd)
            if length < 4:
                break
            signature = readu32(fd)
            if signature == 0xA0000002:
                self.read_console_data_block(fd, length)
            elif signature == 0xA0000004:
                self.read_console_fe_data_block(fd, length)
            elif signature == 0xA0000006:
                self.read_darwin_data_block(fd, length)
            elif signature == 0xA0000001:
                self.read_environment_variable_data_block(fd, length)
            elif signature == 0xA0000007:
                self.read_icon_environment_data_block(fd, length)
            elif signature == 0xA000000B:
                self.read_known_folder_data_block(fd, length)
            elif signature == 0xA0000009:
                self.read_property_store_data_block(fd, length)
            elif signature == 0xA0000008:
                self.read_shim_data_block(fd, length)
            elif signature == 0xA0000010:
                self.read_special_folder_data_block(fd, length)
            elif signature == 0xA0000003:
                self.read_tracker_data_block(fd, length)
            fd.seek(loc + length)

    def read_console_data_block(self, fd, length):
        pass

    def read_console_fe_data_block(self, fd, length):
        pass

    def read_darwin_data_block(self, fd, length):
        pass

    def read_environment_variable_data_block(self, fd, length):
        loc = fd.tell()
        self.ansi_environment_data_block = read_string(fd)
        self.unicode_environment_data_block = read_string(fd, loc + 260)

    def read_icon_environment_data_block(self, fd, length):
        pass

    def read_known_folder_data_block(self, fd, length):
        pass

    def read_property_store_data_block(self, fd, length):
        pass

    def read_shim_data_block(self, fd, length):
        pass

    def read_special_folder_data_block(self, fd, length):
        pass

    def read_tracker_data_block(self, fd, length):
        pass

    def __str__(self):
        s = "ShellLnk:"
        s += "\nLink Flags: %x" % self.link_flags
        s += "\nFile Attributes: %s" % FileAttributeFlags(self.file_attributes).name
        s += "\nCreation time: %s" % self.creation_time.isoformat()
        s += "\nAccess time: %s" % self.access_time.isoformat()
        s += "\nModify time: %s" % self.write_time.isoformat()
        s += "\nFile size: %d" % self.file_size
        if self.link_flags & LinkFlags.has_link_info:
            if self.link_info_flags & LinkInfoFlags.volume_id_and_local_base_path:
                s += "\nVolume label: %s" % self.volume_label
            if self.link_flags & LinkInfoFlags.common_network_relative_link_and_path_suffix:
                s += "\nNet name: %s" % self.net_name
                if self.common_nrl_link_flags & CommonNetworkRelativeLinkFlags.valid_device:
                    s += "\nDevice name: %s" % self.device_name
                if self.common_nrl_link_flags & CommonNetworkRelativeLinkFlags.valid_net_type:
                    s += "\nNet type: %s" % NetworkProviderType(self.network_provider_type).name
            s += "\nCommon suffix: %s" % self.common_base_path_suffix
        if self.link_flags & LinkFlags.has_name:
            s += "\nName: %s" % self.name
        if self.link_flags & LinkFlags.has_relative_path:
            s += "\nRelative path: %s" % self.relative_path
        if self.link_flags & LinkFlags.has_working_dir:
            s += "\nWorking dir: %s" % self.working_dir
        if self.link_flags & LinkFlags.has_arguments:
            s += "\nArguments: %s" % self.command_line_arguments
        if self.link_flags & LinkFlags.has_icon_location:
            s += "\nIcon location: %s" % self.icon_location

        return s
