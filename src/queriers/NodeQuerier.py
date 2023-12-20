import sentinel_protobuf.sentinel.node.v2.querier_pb2 as sentinel_node_v2_querier_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2_grpc as sentinel_node_v2_querier_pb2_grpc 
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import grpc
import urllib.request
import ssl
import threading

class NodeQuerier:
    def __init__(self, channel):
        self.__channel = channel
        self.__default_details_timeout = 10
        self.__ssl_ctx = ssl.create_default_context()
        self.__ssl_ctx.check_hostname = False
        self.__ssl_ctx.verify_mode = ssl.CERT_NONE
        self.__last_nodes_status = {}

    def QueryNode(self, address):
        stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)
        r = stub.QueryNode(sentinel_node_v2_querier_pb2.QueryNodeRequest(address=address))
        return r.node

    def QueryNodes(self, statusEnum):
        fetched_nodes = []
        next_key = 0x01
        stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)

        while(next_key):
            if(next_key == 0x01):
                r = stub.QueryNodes(sentinel_node_v2_querier_pb2.QueryNodesRequest(status=statusEnum))
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(count_total=True,key=next_key)
                r = stub.QueryNodes(sentinel_node_v2_querier_pb2.QueryNodesRequest(status=statusEnum, pagination=next_page_req))

            next_key = r.pagination.next_key
            for n in r.nodes:
                fetched_nodes.append(n)

        return fetched_nodes

    def QueryNumOfNodesWithStatus(self, statusEnum):
        stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)
        r = stub.QueryNodes(sentinel_node_v2_querier_pb2.QueryNodesRequest(status=statusEnum))
        return r.pagination.total

    def QueryNodeStatus(self, node, is_in_thread=False):
        node_endpoint = node.remote_url
        try:
            contents = urllib.request.urlopen(f"{node_endpoint}/status", context = self.__ssl_ctx, timeout=self.__default_details_timeout).read()
            contents = contents.decode('utf-8')
        except urllib.error.URLError as e:
            contents = '{"success":false,"urllib-error":"URLError encountered"}'
        except TimeoutError:
            contents = '{"success":false,"urllib-error":"Data reading timed out"}'
        
        if(is_in_thread):
            self.__last_nodes_status[node.address] = contents
        else:
            return contents

    def QueryAllNodesStatus(self, nodes, n_threads = 8):
        self.__last_nodes_status = {}
        chunks = list(self.__split_into_chunks(nodes, n_threads))
        cur_threads = []
        for c in chunks:
            t = threading.Thread(target=self.__QueryNodesChunk, args=(c,))
            cur_threads.append(t)
            t.start()
        for t in cur_threads:
            t.join()

    def QueryNodesForPlan(self, planid, statusEnum):
        fetched_nodes = []
        next_key = 0x01
        stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)

        while(next_key):
            if(next_key == 0x01):
                r = stub.QueryNodesForPlan(sentinel_node_v2_querier_pb2.QueryNodesForPlanRequest(id=planid, status=statusEnum))
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = stub.QueryNodesForPlan(sentinel_node_v2_querier_pb2.QueryNodesForPlanRequest(id=planid, status=statusEnum, pagination=next_key))

            next_key = r.pagination.next_key
            for n in r.nodes:
                fetched_nodes.append(n)

        return fetched_nodes
        
    def GetCachedNodesStatus(self):
        return self.__last_nodes_status   

    def __QueryNodesChunk(self, chunk):
        for node in chunk:
            self.QueryNodeStatus(node, True)

    def __split_into_chunks(self, l, n):
        for i in range(0, len(l), n):  
            yield l[i:i + n] 

    

if __name__ == "__main__":
    grpc_endpoint = "grpc.sentinel.co:9090"
    channel = grpc.insecure_channel(grpc_endpoint)
    Querier = NodeQuerier(channel)
    active_nodes = Querier.QueryNodes(1)
    Querier.QueryAllNodesStatus(active_nodes)
    Querier.QueryAllNodesStatus(active_nodes)


