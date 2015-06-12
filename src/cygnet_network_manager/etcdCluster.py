import etcd

class EtcdClusterClient(etcd.Client):
    '''
    Etcd cluster client is a client used to manage
    the service information stored in etcd. Information
    stored in etcd match the same information stored in
    the clusterState object
    '''
    def __init__(self, host,nodeId, port=7001, protocol='http'):
        print host
        etcd.Client.__init__(self,host=host, port=port, protocol=protocol)
        print "INIT"
        self.nodeId = str(nodeId)
        print "NODE"

    def _lockNode(self, nodePath):
        ## traverse node path - check any parent nodes are locked.
        free = False
        for i in range(len(nodePath.split("/")),0):
            try:
                lock = self.get("/".join(nodePath.split("/")[:i])+"/lock")
                if lock.value and lock.value != self.nodeId:
                    free &= False
                elif lock.value == None:
                    lock.value = self.nodeId
                    self.update(lock)
                    free &= True
                elif lock.value == self.nodeId:
                    free &= True
            except:
                if i == len(nodePath.split("/")):
                    self.write(nodePath+"/lock",self.nodeId,dir=False)
                else:
                    free &=True
                    continue
        return free

    def _unlockNode(self, nodePath):
        try:
            lock = self.get(nodePath+"/lock")
            lock.value = None
            self.update(lock)
        except:
            return

    def updateContainer(self, container):
        container_key = "nodes/"+ self.nodeId+"/"+container["Id"]
        try:
            for key,value in container.iteritems():
                current_key = container_key + "/" + key
                node = self.get(current_key)
                node.value = container[key]
                self.update(node)
            return True
        except:
            return False
    def updateContainer(self, container, key):
        current_key = "/".join(["nodes",self.nodeId,container["Id"],key])
        try:
            node = self.get(current_key)
            node.value = container[key]
            self.update(node)
            return True
        except:
            return False