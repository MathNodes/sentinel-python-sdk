import ssl
import threading
import urllib.request

import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import sentinel_protobuf.sentinel.node.v2.node_pb2 as node_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2 as sentinel_node_v2_querier_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2_grpc as sentinel_node_v2_querier_pb2_grpc


class NodeQuerier:
    def __init__(self, channel, status_fetch_timeout: int):
        self.status_fetch_timeout = status_fetch_timeout
        self.__channel = channel
        self.__stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)
        self.__ssl_ctx = ssl.create_default_context()
        self.__ssl_ctx.check_hostname = False
        self.__ssl_ctx.verify_mode = ssl.CERT_NONE
        self.__nodes_status_cache = {}

    def QueryNode(self, address: str):
        r = self.__stub.QueryNode(
            sentinel_node_v2_querier_pb2.QueryNodeRequest(address=address)
        )
        return r.node

    def QueryNodes(self, statusEnum: int):
        fetched_nodes = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryNodes(
                    sentinel_node_v2_querier_pb2.QueryNodesRequest(status=statusEnum)
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryNodes(
                    sentinel_node_v2_querier_pb2.QueryNodesRequest(
                        status=statusEnum, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for n in r.nodes:
                fetched_nodes.append(n)

        return fetched_nodes

    def QueryNumOfNodesWithStatus(self, statusEnum: int):
        r = self.__stub.QueryNodes(
            sentinel_node_v2_querier_pb2.QueryNodesRequest(status=statusEnum)
        )
        return r.pagination.total

    def QueryNodeStatus(self, node: node_pb2.Node, is_in_thread=False):
        node_endpoint = node.remote_url
        try:
            contents = urllib.request.urlopen(
                f"{node_endpoint}/status",
                context=self.__ssl_ctx,
                timeout=self.status_fetch_timeout,
            ).read()
            contents = contents.decode("utf-8")
        except urllib.error.URLError:
            contents = '{"success":false,"urllib-error":"URLError encountered"}'
        except TimeoutError:
            contents = '{"success":false,"urllib-error":"Data reading timed out"}'

        if is_in_thread:
            self.__nodes_status_cache[node.address] = contents
        else:
            return contents

    def QueryNodesStatus(self, nodes: list[node_pb2.Node], n_threads=8):
        chunks = list(self.__split_into_chunks(nodes, n_threads))
        cur_threads = []
        for c in chunks:
            t = threading.Thread(target=self.__QueryNodesChunk, args=(c,))
            cur_threads.append(t)
            t.start()
        for t in cur_threads:
            t.join()

        result = self.__nodes_status_cache
        self.__nodes_status_cache = {}

        return result

    def QueryNodesForPlan(self, plan_id: int, statusEnum: int):
        fetched_nodes = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryNodesForPlan(
                    sentinel_node_v2_querier_pb2.QueryNodesForPlanRequest(
                        id=plan_id, status=statusEnum
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryNodesForPlan(
                    sentinel_node_v2_querier_pb2.QueryNodesForPlanRequest(
                        id=plan_id, status=statusEnum, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for n in r.nodes:
                fetched_nodes.append(n)

        return fetched_nodes

    def __QueryNodesChunk(self, chunk: list[node_pb2.Node]):
        for node in chunk:
            self.QueryNodeStatus(node, True)

    def __split_into_chunks(self, items: list, size: int):
        for i in range(0, len(items), size):
            plus = i + size
            yield items[i:plus]
            # https://github.com/PyCQA/pycodestyle/issues/373
