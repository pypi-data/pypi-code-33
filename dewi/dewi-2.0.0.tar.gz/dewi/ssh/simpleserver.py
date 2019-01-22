import socketserver
import typing


class SimpleSshServer:

    def __init__(self, handler: typing.Type[socketserver.BaseRequestHandler],
                 *,
                 listening_address: str = '127.0.0.1',
                 listening_port: int = 22):
        self.listening_address = listening_address
        self.listening_port = listening_port
        self.handler = handler

    def run(self):
        with socketserver.TCPServer((self.listening_address, self.listening_port), self.handler) as server:
            server.serve_forever()


if __name__ == '__main__':
    from handler import SshHandler

    #//SimpleSshServer(SshHandler, listening_port=4).run()
    print('X')

    TROUBLESHOOTING_ACTIONS = {
        'last.out.txt': {
            'command': 'last',
        },
        'cl_status.out.txt': {
            'command': 'cl_status rscstatus -m',
        },
        'proc-drbd.out.txt': {
            'command': 'cat /proc/drbd',
        },
        'proc-interrupts.out.txt': {
            'command': 'cat /proc/interrupts',
        },
        'proc-locks.out.txt': {
            'command': 'cat /proc/locks',
        },
        'proc-meminfo.out.txt': {
            'command': 'cat /proc/meminfo',
        },
        'proc-mounts.out.txt': {
            'command': 'cat /proc/mounts',
        },
        'proc-swaps.out.txt': {
            'command': 'cat /proc/swaps',
        },
        'proc-vmallockinfo.out.txt': {
            'command': 'cat /proc/vmallocinfo',
        },
        'proc-limits.out.txt': {
            'command': 'cat /proc/self/limits',
        },
        'netstat.apen.out.txt': {
            'command': 'netstat -apen',
        },
        'proc-dev-raid.txt': {
            'command': 'for i in `find /proc/sys/dev/raid/ -type f`; do'
                       '    echo "### $i";'
                       '    cat "$i";'
                       '    echo "\n";'
                       'done',
        },
        'proc-scsi.txt': {
            'command': 'for i in `find /proc/scsi/ -type f`; do'
                       '    echo "### $i";'
                       '    cat "$i";'
                       '    echo "\n";'
                       'done',
        },
        'proc-bus.txt': {
            'command': 'for i in `find /proc/bus/ -name devices -type f`; do'
                       '    echo "### $i";'
                       '    cat "$i";'
                       '    echo "\n";'
                       'done',
        },
        'proc-fs.txt': {
            'command': 'for i in `find /proc/fs/ -type f`; do'
                       '    echo "### $i";'
                       '    cat "$i";'
                       '    echo "\n";'
                       'done',
        },
        'proc-net.txt': {
            'command': 'for i in `find /proc/net/ -type f`; do'
                       '    echo "### $i";'
                       '    cat "$i";'
                       '    echo "\n";'
                       'done',
        },
        'ifconfig.out.txt': {
            'command': 'ifconfig',
        },
        'fdisk.l.out.txt': {
            'command': 'fdisk -l',
            'hardware_types': [
                'virtual',
            ],
        },
        'sgdisk.p.out.txt': {
            'command': 'ls -1 /dev/'
                       '| grep -E \'^([vsh]|xv)d[a-z]+$\''
                       '| sort'
                       '| while read disk; do'
                       '    sgdisk -p "/dev/${disk}";'
                       'done',
            'hardware_types': [
                'T1',
                'T4',
                'T10',
                'virtual',
            ],
        },
        'free.out.txt': {
            'command': 'free',
        },
        'route.n.out.txt': {
            'command': 'route -n',
        },
        'ip.rule.show.out.txt': {
            'command': 'ip rule show',
        },
        'ip.route.show.table.all.out.txt': {
            'command': 'ip route show table all',
        },
        'ip.link.show.out.txt': {
            'command': 'ip link show',
        },
        'ip.route.show.out.txt': {
            'command': 'ip route show',
        },
        'ip.addr.show.out.txt': {
            'command': 'ip addr show',
        },
        'df.h.out.txt': {
            'command': 'df -h',
        },
        'ps.auxf.out.txt': {
            'command': 'ps auxf',
        },
        'ethtool.eth0.out.txt': {
            'command': 'ethtool eth0',
        },
        'ethtool.eth1.out.txt': {
            'command': 'ethtool eth1',
        },
        'ethtool.eth2.out.txt': {
            'command': 'ethtool eth2',
        },
        'ethtool.eth3.out.txt': {
            'command': 'ethtool eth3',
        },
        'ethtool.eth4.out.txt': {
            'command': 'ethtool eth4',
            'hardware_types': [
                'T10',
            ],
        },
        'ethtool.eth5.out.txt': {
            'command': 'ethtool eth5',
            'hardware_types': [
                'T10',
            ],
        },
        'ethtool.S.eth0.out.txt': {
            'command': 'ethtool -S eth0'
        },
        'ethtool.S.eth1.out.txt': {
            'command': 'ethtool -S eth1'
        },
        'ethtool.S.eth2.out.txt': {
            'command': 'ethtool -S eth2'
        },
        'ethtool.S.eth3.out.txt': {
            'command': 'ethtool -S eth3'
        },
        'ethtool.S.eth4.out.txt': {
            'command': 'ethtool -S eth4',
            'hardware_types': [
                'T10',
            ],
        },
        'ethtool.S.eth5.out.txt': {
            'command': 'ethtool -S eth5',
            'hardware_types': [
                'T10',
            ],
        },
        'services.boot.svg': {
            'command': 'systemd-analyze plot',
        },
        'mdstat.out.txt': {
            'command': 'cat /proc/mdstat',
            'hardware_types': [
                'T1',
            ],
        },
        'boot.systemctl.status.txt': {
            'command': '/bin/systemctl status --all --full',
        },
        'boot.systemctl.state_failed.txt': {
            'command': '/bin/systemctl --state=failed --full',
        },
        'boot_reboot_journal.txt': {
            'command': 'cat /var/log/boot_reboot_journal.txt',
        },
        'nodeid.out.txt': {
            'command': 'cat /etc/ssb/nodeid',
        },
        'smartctl.swraid.disks.out.txt': {
            'command': 'ls -1 /dev/'
                       '| grep -E \'^[sh]d[a-z]+$\''
                       '| sort'
                       '| while read disk; do'
                       '    echo "### Disk: ${disk}";'
                       '    smartctl -x "/dev/${disk}";'
                       '    echo "\n";'
                       'done',
            'hardware_types': [
                'T1',
            ],
        },
        'smartctl.hwraid-mbx.disks.out.txt': {
            'command': 'storcli /c0 /eall /sall show'
                       '| awk \'/^[0-9].*(Onln|UGood)/ {print $2;}\''
                       '| sort -n'
                       '| while read disk_id; do'
                       '    echo "### Disk ID: ${disk_id}";'
                       '    smartctl -T permissive -x -d "megaraid,${disk_id}" /dev/sda;'
                       '    echo "\n";'
                       'done',
            'hardware_types': [
                'T4',
                'T10',
            ],
        },
        'dmidecode': {
            'command': 'dmidecode',
        },
        'hardware_type.txt': {
            'function': 'xcb_get_hardware_config',
        },
        'ha_drbd.txt': {
            'function': 'xcb_get_drbd_status',
        },
        'ha_redundant.txt': {
            'function': 'xcb_get_redundant_ha_infos',
        },
        'ipmi.out.txt': {
            'function': 'xcb_get_ipmi_info',
        },
        'boot_extra.txt': {
            'function': 'xcb_check_boot_files',
        },
        'core_extra.txt': {
            'function': 'xcb_check_core_files',
        },
        'lsi_get_output.txt': {
            'function': 'xcb_lsi_get',
            'hardware_types': [
                'T4',
                'T10',
            ],
            'section': 'raid',
        },
        'lsi_show_all.txt': {
            'command': 'storcli /c0 show all',
            'hardware_types': [
                'T4',
                'T10',
            ],
            'section': 'raid',
        },
        'bash_history.boot.txt': {
            'command': 'cat /root/.bash_history',
        },
        'bash_history.core.txt': {
            'command': 'cat /mnt/firmware/root/.bash_history',
        },
    }

    import json


    with open('/tmp/a.json', 'w') as f:

        json.dump(TROUBLESHOOTING_ACTIONS, f, indent=4)

