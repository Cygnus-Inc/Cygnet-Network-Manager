from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks
from cygnet_network_manager.clusterState import ClusterState
import uuid


class Client(ApplicationSession):
    '''
    Client is used to connect to the router
    all Helpers should connect to the router
    since some directives are being passed through
    PUB/SUB topics.
    Moreover, the Client obtains or create a new
    node id to use later. The id is also used by the
    adapter. using a unified id an ovs helper can find
    which adapter it corresponds to amongst the running
    adapters
    '''
    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.cluster_state = ClusterState(self)
        try:
            self.node_id = (open('/cygnus/node', 'r')).read()
        except IOError:
            self.node_id = str(uuid.uuid1())
            f = open('/cygnus/node', 'w')
            f.write(self.node_id)
            f.close()

    @inlineCallbacks
    def onJoin(self, details):

        print "Helper Attached to Router"
        self.cluster_state.init()
        yield self.subscribe(self.cluster_state)

    def leave(self, reason=None, log_message=None):
        ApplicationSession.leave(self, reason, log_message)

    def disconnect(self):
        ApplicationSession.disconnect(self)
