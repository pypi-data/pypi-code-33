import click


def get_interfaces(conn, ip_address):
    filtering = {
        'resource': 'ec2_network_interface',
    }
    interfaces = conn.find(filtering)

    interfaces = [
        i for i in interfaces
        if (
                   'PrivateIpAddress' in i and
                   ip_address == i['PrivateIpAddress']
           ) or (
                   'Association' in i and
                   'PublicIp' in i['Association'] and
                   ip_address == i['Association']['PublicIp']
           )
    ]

    [i.update({'aws_profile': conn.profile}) for i in interfaces]

    return interfaces


@click.argument('address', default=False)
@click.command()
def ip(address):
    """Find ip in aws account(s)"""
    from awssearch.config import connections

    o = []
    if address:
        for conn in connections:
            o += get_interfaces(conn, address)

    else:
        import sys
        for line in sys.stdin:
            address = line.replace('\n', '')
            for conn in connections:
                o += get_interfaces(conn, address)

    from awssearch.output import output
    output(o)


if __name__ == '__main__':
    ip()
