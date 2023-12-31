import ssl
import threading
import urllib.request
from typing import Any

import grpc
import sentinel_protobuf.sentinel.node.v2.node_pb2 as node_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2 as sentinel_node_v2_querier_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2_grpc as sentinel_node_v2_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest


class NodeQuerier(Querier):
    def __init__(self, channel: grpc.Channel, status_fetch_timeout: int):
        self.status_fetch_timeout = status_fetch_timeout
        self.__stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(channel)

        # Disable SSL verification
        self.__ssl_ctx = ssl.create_default_context()
        self.__ssl_ctx.check_hostname = False
        self.__ssl_ctx.verify_mode = ssl.CERT_NONE

        self.__nodes_status_cache = {}

    def QueryNode(self, address: str) -> Any:
        r = self.__stub.QueryNode(
            sentinel_node_v2_querier_pb2.QueryNodeRequest(address=address)
        )
        return r.node

    def QueryNodes(self, status: int, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QueryNodes,
            request=sentinel_node_v2_querier_pb2.QueryNodesRequest,
            attribute="nodes",
            status=status.value,
            pagination=pagination,
        )

    def QueryNumOfNodesWithStatus(self, status: int) -> int:
        r = self.__stub.QueryNodes(
            sentinel_node_v2_querier_pb2.QueryNodesRequest(status=status.value)
        )
        return r.pagination.total

    def QueryNodeStatus(self, node: node_pb2.Node, is_in_thread: bool = False) -> str:
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

    def QueryNodesStatus(self, nodes: list[node_pb2.Node], n_threads: int = 8) -> dict:
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

    def QueryNodesForPlan(
        self, plan_id: int, status: int, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QueryNodesForPlan,
            request=sentinel_node_v2_querier_pb2.QueryNodesForPlanRequest,
            attribute="nodes",
            status=status.value,
            id=plan_id,
            pagination=pagination,
        )

    def __QueryNodesChunk(self, chunk: list[node_pb2.Node]):
        for node in chunk:
            self.QueryNodeStatus(node, True)

    def __split_into_chunks(self, items: list, size: int):
        for i in range(0, len(items), size):
            plus = i + size
            yield items[i:plus]
            # https://github.com/PyCQA/pycodestyle/issues/373
