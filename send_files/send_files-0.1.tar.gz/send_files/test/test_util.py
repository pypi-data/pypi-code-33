from ..util import _hosts

data = (
    {
        24: [
            {'addr': '::1', 'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128'},
            {'addr': 'fe80:4::1', 'netmask': 'ffff:ffff:ffff:ffff::/64'},
        ],
        2: [
            {'addr': '127.0.0.1'},
        ]
    },
    {
        18: [
            {'addr': '00:00:00:00:00:00'},
        ],
        2: [
            {'addr': '192.168.2.2', 'netmask': '255.255.255.0', 'broadcast': '192.168.2.255'},
        ],
    },
    {
        18: [
            {'addr': '88:88:88:88:88:88'},
        ],
    },
    {},
    {},
)

def test_hosts():
    assert tuple(_hosts(data)) == ('[::1]', '[fe80:4::1]', '127.0.0.1', '192.168.2.2')
