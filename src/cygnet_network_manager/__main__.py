import sys
import click
from cygnet_network_manager.helper import Helper
# Why does this file exist, and why __main__?
# For more info, read:
# - https://www.python.org/dev/peps/pep-0338/
# - https://docs.python.org/2/using/cmdline.html#cmdoption-m
# - https://docs.python.org/3/using/cmdline.html#cmdoption-m

usage = '''[Usage]
--router-addr       : the wamp router address (e.g. '0.0.0.0')
--etcd-server-addr  : address of etcd node to read cluster state from (e.g. '0.0.0.0:7001')
--internal-network  : type of the internal network type to use (e.g. OpenvSwitch)
--internal-addr     : the address of the internal network (e.g. '10.1.3.1/16')
--router-realm      : crossbar router realm to join (e.g. 'cygnet')
'''


def validate_router_addr(ctx, param, value):
    # If address is not formatted correctly or illegal port is provided
    # etcdClient will complain so no need to worry about it
    if not value:
        print(usage)
        raise click.MissingParameter('--router-addr is missing')
    return value


def validate_etcd_addr(ctx, param, value):
    if len(value.split(':')) != 2:
        print(usage)
        raise click.BadParameter('--etcd-server-addr is formatted incorrectly')
    try:
        int(value.split(':')[1])
    except:
        print(usage)
        raise click.BadParameter('--etcd-addr has illegal port number provided')
    return value


def validate_net_type(ctx, param, value):
    net_types = ['openvswitch']
    if value.lower() not in net_types:
        print(usage)
        raise click.BadParameter('--internal-network Illegal type provided or not yet implemented')
    return value


def validate_ip(ctx, param, value):
    if not value:
        print(usage)
        raise click.MissingParameter('--internal-addr is missing')
    if len(value.split('/')) != 2:
        print(usage)
        raise click.BadParameter('--internal-addr illegal address provided')
    port = value.split('/')[1]
    addr = value.split('/')[0]
    if len(addr.split('.')) == 4:
        print(usage)
        raise click.BadParameter('--internal-addr illegal address provided')
    try:
        port = int(port)
    except:
        print(usage)
        raise click.BadParameter('--internal-addr illegal address provided')

    if port >= 32 or port <= 0:
        print(usage)
        raise click.BadParameter('--internal-addr illegal address provided')

    for octet in addr.split('.'):
        try:
            octet = int(octet)
            if octet >= 256 or octet < 0:
                raise Exception
        except:
            print(usage)
            raise click.BadParameter('--internal-addr illegal address provided')
    return value


@click.command()
@click.option('--router-addr', envvar='CYGNET_CROSSBAR_ADDR', callback=validate_router_addr)
@click.option('--router-realm', envvar='CYGNET_CROSSBAR_REALM', default='cygnet')
@click.option('--etcd-server-addr', envvar='CYGNET_ETCD_ADDR', default='0.0.0.0:7001', callback=validate_etcd_addr)
@click.option('--internal-network', envvar='CYGNET_INTERNAL_TYPE', default='OpenvSwitch', callback=validate_net_type)
@click.option('--internal-addr', envvar='CYGNET_INTERNAL_IP')
def main(router_addr, router_realm, etcd_server_addr, internal_network, internal_addr):
    print(etcd_server_addr)
    kwargs = {'router-addr': router_addr,
              'internal-addr': internal_addr,
              'etcd-server-addr': tuple(etcd_server_addr.split(":")),
              'internal-network': internal_network,
              'router-realm': router_realm
              }
    print(kwargs)
    helper = Helper(**kwargs)
    helper.connect()

if __name__ == "__main__":
    sys.exit(main())
