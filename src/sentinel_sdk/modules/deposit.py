from typing import Any

import grpc
import sentinel_protobuf.sentinel.deposit.v1.querier_pb2 as sentinel_deposit_v1_querier_pb2
import sentinel_protobuf.sentinel.deposit.v1.querier_pb2_grpc as sentinel_deposit_v1_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest


class DepositModule(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_deposit_v1_querier_pb2_grpc.QueryServiceStub(channel)

    def QueryDeposit(self, address: str) -> Any:
        try:
            r = self.__stub.QueryDeposit(
                sentinel_deposit_v1_querier_pb2.QueryDepositRequest(address=address)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.deposit

    def QueryDeposits(self, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QueryDeposits,
            request=sentinel_deposit_v1_querier_pb2.QueryDepositsRequest,
            attribute="deposits",
            pagination=pagination,
        )
