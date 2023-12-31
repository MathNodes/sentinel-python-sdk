from typing import Any

import grpc
import sentinel_protobuf.sentinel.provider.v2.querier_pb2 as sentinel_provider_v2_querier_pb2
import sentinel_protobuf.sentinel.provider.v2.querier_pb2_grpc as sentinel_provider_v2_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest


class ProviderQuerier(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_provider_v2_querier_pb2_grpc.QueryServiceStub(channel)

    def QueryProvider(self, address: str) -> Any:
        try:
            r = self.__stub.QueryProvider(
                sentinel_provider_v2_querier_pb2.QueryProviderRequest(address=address)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.provider

    def QueryProviders(self, status: int, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QueryProviders,
            request=sentinel_provider_v2_querier_pb2.QueryProvidersRequest,
            attribute="providers",
            status=status.value,
            pagination=pagination,
        )
