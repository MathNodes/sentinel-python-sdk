from typing import Any

import grpc
import sentinel_protobuf.sentinel.swap.v1.querier_pb2 as sentinel_swap_v1_querier_pb2
import sentinel_protobuf.sentinel.swap.v1.querier_pb2_grpc as sentinel_swap_v1_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest

# import sentinel_protobuf.sentinel.swap.v1.swap_pb2 as swap_pb2


class SwapQuerier(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_swap_v1_querier_pb2_grpc.QueryServiceStub(channel)

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
