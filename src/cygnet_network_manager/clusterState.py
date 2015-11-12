from copy import deepcopy
from autobahn import wamp
from cygnet_common.design import Task
from cygnet_network_manager.etcdCluster import EtcdClusterClient


class ClusterState(object):
    '''
    an Cluster state is merely an object which
    implements few pub/sub methods. those methods
    are mainly for synchronizing the ovs helpers
    which are up in the moment and hold its properties
    every helper has a fork of these information to avoid
    SPoF.
    Once a helper is ready to join a cluster it makes a
    synchronization request. once other helpers receive
    that request they broadcast the helpers properties
    structure they hold. Thus, a request issuer initialize
    its structure and create gre tunnel to each helper
    Moreover a health check is made on an interval
    if a helper didn't respond for a few intervals
    it is deemed unhealthy and removed.
    an extra subscriber method is "hookContainer" which
    merely invokes pipework to hook a container received.

    Changes:
        Mainly all changes will occur here since our network
        compontents will be limited to endpoints, intefaces
        and containers which are manipulated by cygnet_common
        we won't need to manipulate them here, But refactor the
        code to a more generic code.
        We also might have to remove the data synchronization
        instead we can merely update and construct the layout
        over etcd as per components mentioned.

        values currently communicated via wamp are endpoints info
        and number in order to maintain properly network setup such as:
            tunnel names, remote ip addresses, container hooking
            directives..etc
        these values will be also communicated via etcd to construct a
        non-horizontal representation of the network.
    '''
    address1 = None
    interface = None
    etcd_addr = None

    def __init__(self, session):
	'''
        At initialization interface is supposed to be
        previously initialized and set as a class variable
        so we won't have to set containers or endpoints since
        they're held by the cygnetcommon interface.
        '''
        self.session = session
        self.gre_endpoint = self.address1
        self.gre_health = dict()

    def init(self):
        '''
        On initialization a mere sync request is sent and
        components are set to action.
        '''
        self.session.publish("ovs.sync_request", self.gre_endpoint[0])
        self.health_check = Task.TaskInterval(10, self.keepalive)
        self.health_check.start()
        self.etcd_client = EtcdClusterClient(self.etcd_addr[0], self.session.node_id, int(self.etcd_addr[1]))

    def keepalive(self):
        self.session.publish("ovs.sync_request", self.gre_endpoint[0])
        try:
            most = max([health for health in self.gre_health.itervalues()])
        except ValueError as e:
            print e
            return
        gre_health_tmp = deepcopy(self.gre_health)
        for gre_endpoint, health in gre_health_tmp.iteritems():
            mask = [endpoint == gre_endpoint for endpoint in self.interface.endpoints]
            if (most - health) > 5 and sum(mask):
                # unhealthy endpoint -- remove
                idx = mask.index(True)
                self.interface.endpoints.pop(idx)
                self.gre_health.pop(gre_endpoint)
                # Broadcast modifications
                self.session.publish("ovs.sync_nodes", self.interface.endpoints)

    # What should we sync?
    # 1- GRE endpoints
    @wamp.subscribe(u'ovs.sync_nodes')
    def syncNodes(self, gre_endpoints):
        print "Syncing: ", gre_endpoints
        # Are we starting up?
        # a properly sat up cluster with more than two nodes will be refering
        # to the same number of endpoints
        # a one-node cluster should receive a full list of same up
        # endpoints from another
        if len(self.interface.endpoints) == 0 and len(gre_endpoints) != 0:
            self.interface.initContainerNetwork()
            for endpoint in gre_endpoints:
                self.interface.endpoints.append(endpoint)
        # Are we broadcasting new endpoint(s)
        elif len(self.interface.endpoints) < len(gre_endpoints):
            for gre_endpoint in gre_endpoints:
                if gre_endpoint not in self.interface.endpoints:
                    self.interface.endpoints.append(gre_endpoint)

        # Are we broadcasting endpoint leave?
        elif len(gre_endpoints) < len(self.interface.endpoints) and len(gre_endpoints) != 0:
            for gre_endpoint in self.interface.endpoints:
                if gre_endpoint not in gre_endpoints:
                    self.interface.endpoints.remove(gre_endpoint)

        # If we reach this point without updating GRE we're the second node up
        # We should act as the first GRE endpoint and re-broadcast
        # We don't have to update gre since Network Interface will do that for us
        # self.update_gre()
        print "Synced:", self.interface
        print "ME:", self.gre_endpoint

    @wamp.subscribe(u'ovs.sync_request')
    def syncRequest(self, origin):
        print "Request.."
        # we don't really care who issued
        if origin:
            if origin not in self.gre_health:
                self.gre_health[origin] = 0
            if len(self.interface.endpoints) == 0:
                self.interface.initContainerNetwork()
            if origin not in self.interface.endpoints:
                self.interface.endpoints.append(origin)
                to_sync = (self.interface.endpoints[:self.interface.endpoints.index(origin)] +
                           self.interface.endpoints[self.interface.endpoints.index(origin)+1:] +
                           [self.gre_endpoint[0]])
                self.session.publish("ovs.sync_nodes", to_sync)
            self.gre_health[origin] += 1
            self.gre_health[origin] = max([v for v in self.gre_health.itervalues()])

    @wamp.subscribe(u'ovs.hook_container')
    def hookContainer(self, container):
        if str(container["Node"]) != self.session.node_id:
            return
        print container
        if container["Address"]:
            self.interface.containers.append(container)
            return
        return

    @wamp.subscribe(u'ovs.unhook_container')
    def unhookContainer(self, container):
        if str(container["Node"]) != self.session.node_id:
            return
        if container["Address"]:
            for idx in range(len(self.interface.containers)):
                if self.interface.containers[idx]["Id"] == container["Id"]:
                    self.interface.containers.pop(idx)
