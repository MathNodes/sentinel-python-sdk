import ssl
import threading
import urllib.parse
import urllib.request
from typing import Any
import json
import uuid
import base64
import hashlib
import ecdsa
import grpc
import sentinel_protobuf.sentinel.node.v2.node_pb2 as node_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2 as sentinel_node_v2_querier_pb2
import sentinel_protobuf.sentinel.node.v2.querier_pb2_grpc as sentinel_node_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.node.v2.msg_pb2 as msg_pb2

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams, NodeType

from pywgkey import WgKey


class NodeModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, node_timeout: int, account, client):
        self.node_timeout = node_timeout
        self.__stub = sentinel_node_v2_querier_pb2_grpc.QueryServiceStub(channel)

        # Disable SSL verification
        self.__ssl_ctx = ssl.create_default_context()
        self.__ssl_ctx.check_hostname = False
        self.__ssl_ctx.verify_mode = ssl.CERT_NONE

        self._account = account
        self._client = client

        self.__nodes_status_cache = {}

    def QueryParams(self) -> Any:
        return self.__stub.QueryParams(sentinel_node_v2_querier_pb2.QueryParamsRequest()).params

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
                timeout=self.node_timeout,
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

    def RegisterNode(self, gigabyte_prices: int, hourly_prices: int, remote_url: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgRegisterRequest(
            frm = self._account.address,
            gigabyte_prices=gigabyte_prices,
            hourly_prices=hourly_prices,
            remote_url=remote_url,
        )
        return self.transaction([msg], tx_params)

    def SubscribeToNode(self, node_address: str, gigabytes: int = 0, hours: int = 0, denom: str = "udvpn", tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgSubscribeRequest(
            frm = self._account.address,
            denom = denom,
            gigabytes = gigabytes,
            hours = hours,
            node_address = node_address,
        )
        return self.transaction([msg], tx_params)

    def UpdateNodeDetails(self, gigabyte_prices: int, hourly_prices: int, remote_url: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateDetailsRequest(
            frm = self._account.address,
            gigabyte_prices = gigabyte_prices,
            hourly_prices = hourly_prices,
            remote_url = remote_url,
        )
        return self.transaction([msg], tx_params)

    def UpdateNodeStatus(self, status: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateStatusRequest(
            frm = self._account.address,
            status = status.value,
        )
        return self.transaction([msg], tx_params)

    def __post_session(self, url: str, payload: dict) -> str:
        request = urllib.request.Request(url)
        request.add_header("Content-Type", "application/json; charset=utf-8")
        json_data_bytes = json.dumps(payload).encode("utf-8")  # needs to be bytes
        request.add_header("Content-Length", len(json_data_bytes))
        # TODO: status code != 200 was not handled
        with urllib.request.urlopen(request, json_data_bytes, timeout=self.node_timeout, context=self.__ssl_ctx) as f:
            return f.read().decode("utf-8")

    # TODO: find another 'fancy' name
    def PostSession(
        self, session_id: int, remote_url: str, node_type: NodeType = NodeType.WIREGUARD
    ):
        if node_type == NodeType.WIREGUARD:
            # [from golang] wgPrivateKey, err = wireguardtypes.NewPrivateKey()
            # [from golang] key = wgPrivateKey.Public().String()
            wgkey = WgKey()
            # The private key should be used by the wireguard client
            key = wgkey.pubkey
        else:  # NodeType.V2RAY
            # os.urandom(16)
            # [from golang] uid, err = uuid.GenerateRandomBytes(16)
            # [from golang] key = base64.StdEncoding.EncodeToString(append([]byte{0x01}, uid...))
            key = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")

        # append([]byte{0x01}, uid) is required)
        # The key of wireguard is 32 bytes length, for v2ray only 16?

        # self._account inherited from Transactor class.
        # self._account.private_key and self._account.address

        sk = ecdsa.SigningKey.from_string(
            self._account.private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256
        )

        session_id = int(session_id)
        # Uint64ToBigEndian
        bige_session = session_id.to_bytes(8, "big")
        signature = sk.sign(bige_session)

        payload = {
            "key": key,
            "signature": base64.b64encode(signature).decode("utf-8"),
        }
        return self.__post_session(
            f"{remote_url}/accounts/{self._account.address}/sessions/{session_id}",
            payload,
        )