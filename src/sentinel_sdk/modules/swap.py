from typing import Any

import grpc
import sentinel_protobuf.sentinel.swap.v1.querier_pb2 as sentinel_swap_v1_querier_pb2
import sentinel_protobuf.sentinel.swap.v1.querier_pb2_grpc as sentinel_swap_v1_querier_pb2_grpc
import sentinel_protobuf.sentinel.swap.v1.msg_pb2 as msg_pb2

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams

# import sentinel_protobuf.sentinel.swap.v1.swap_pb2 as swap_pb2


class SwapModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, client):
        self.__stub = sentinel_swap_v1_querier_pb2_grpc.QueryServiceStub(channel)
        self._account = account
        self._client = client

    def QuerySwap(self, tx_hash: bytes) -> Any:
        try:
            r = self.__stub.QuerySwap(
                sentinel_swap_v1_querier_pb2.QuerySwapRequest(tx_hash=tx_hash)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.swap

    def QuerySwaps(self, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySwaps,
            request=sentinel_swap_v1_querier_pb2.QuerySwapsRequest,
            attribute="swaps",
            pagination=pagination,
        )
    
    def Swap(self, amount: str, receiver: str, tx_hash: bytes, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgSwapRequest(
            frm = self._account.address,
            amount = amount,
            receiver = receiver,
            tx_hash = tx_hash,
        )
        return self.transaction([msg], tx_params)