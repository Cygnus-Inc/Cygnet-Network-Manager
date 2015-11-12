"""
This module contains python functions that wrap shell commands.
"""
from __future__ import print_function


def pipework(*args, **kwargs):
    """
    The basic, flexible wrapper around the pipework function.

    This checks that we have the required inputs neccessary for
    pipework to function before attempting to execute anything.
    After we are sure that the minimum parameters are provided,
    we can unpack the function's kwargs and build the shell
    command.
    """

    # Docker integration
    # docker run -name web1 -d apache
    # pipework br1 web1 192.168.12.23/24

    # Peeking inside the private network
    # ip addr add 192.168.1.254/24 dev br1

    # Setting container internal interface
    # pipework br1 -i eth2 ...

    # Setting host interface name
    # pipework br1 -i eth2 -l hostapp1 ...

    # Setting a default gateway
    # pipework br1 $CONTAINERID 192.168.4.25/20@192.168.4.1

    # Connect a container to a local physical interface
    # pipework eth2 $(docker run -d hipache /usr/sbin/hipache) 50.19.169.157/24
    # pipework eth3 $(docker run -d hipache /usr/sbin/hipache) 107.22.140.5/24

    # Specify a custom MAC address
    # pipework eth0 $(docker run -d haproxy) 192.168.1.2/24 26:2e:71:98:60:8f
    # pipework br0 $(docker run -d zerorpcworker) dhcp fa:de:b0:99:52:1c

    # Support Open vSwitch
    # ovs-vsctl list-br
    # ovsbr0
    # pipework ovsbr0 $(docker run -d mysql /usr/sbin/mysqld_safe) 192.168.1.2/24  # noqa

    # "Syntax:"
    # "pipework <hostinterface> [-i containerinterface] [-l localinterfacename] <guest> <ipaddr>/<subnet>[@default_gateway] [macaddr][@vlan]"  # noqa
    # "pipework <hostinterface> [-i containerinterface] [-l localinterfacename] <guest> dhcp [macaddr][@vlan]"  # noqa
    # "pipework --wait [-i containerinterface]"

    keys = [
        'host_interface',
        'container_interface',
        'local_interface_name',
        'guest',
        'ip_address',
        'subnet',
        'default_gateway',
        'mac_address',
        'dhcp',
        'wait',
    ]

    if not set(kwargs.keys()) < set(keys):
        # This tests that we havent been given any kwargs that the function
        # doesnt know how to handle.
        # At the moment, this does nothing, but it might be useful to
        # raise an error.
        pass

    cmd_parts = list()
    cmd_parts.append('pipework')

    if 'host_interface' in kwargs:
        pass
    if 'container_interface' in kwargs:
        pass
    if 'local_interface_name' in kwargs:
        pass
    if 'guest' in kwargs:
        pass
    if 'ip_address' in kwargs:
        pass
    if 'subnet' in kwargs:
        pass
    if 'default_gateway' in kwargs:
        pass
    if 'mac_address' in kwargs:
        pass

    # if 'bridge_name' in kwargs:
    #     pass
    # if 'docker_container_id' in kwargs:
    #     pass
    # if 'docker_container_name' in kwargs:
    #     pass
    # if 'eth0' in kwargs:
    #     # Interface options are grouped into a dict.
    #     pass
    # if 'eth1' in kwargs:
    #     # Interface options are grouped into a dict.
    #     pass
    # if 'mac_address' in kwargs:
    #     pass
    cmd = ''.join(cmd_parts)
    print(cmd)

    # br2 -i eth0 $1 $ADDRESS/16@$GATEWAY'
