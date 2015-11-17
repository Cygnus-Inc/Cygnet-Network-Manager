from cygnet_network_manager.client import Client
from cygnet_network_manager.clusterState import ClusterState
from autobahn.twisted.wamp import ApplicationRunner
from cygnet_common.NetworkInterface import NetworkInterface
from cygnet_common import strtypes

class Helper(object):

    # get the address of br1 supposed that ovs ifaces are up
    def __init__(self, **kwargs):
        # Obtain network information
        self.args = dict()
        for arg, value in kwargs.iteritems():
            self.args[arg] = value
        print(self.args)
        empty_setup = {'interfaces': [],
                       'containers': [],
                       'endpoints': [],
                       'interface_class': self.args['internal-network'],
                       'internal_ip': self.args['internal-addr']
                       }
        interface = NetworkInterface(**empty_setup)
    # address is returned as a 2-tuple of strings addr,mask
        self.address = interface.initalize()
        ClusterState.address1 = self.address
        ClusterState.interface = interface
        ClusterState.etcd_addr = self.args['etcd-server-addr']

    # simply run the client
    def connect(self):
        print(self.args['router-addr'])
        runner = ApplicationRunner(u"ws://" + self.args['router-addr'] + "/ws", strtypes.cast_unicode(self.args['router-realm']))
        runner.run(Client)
