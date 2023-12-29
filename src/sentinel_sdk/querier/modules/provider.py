from typing import Any

import grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import sentinel_protobuf.sentinel.provider.v2.querier_pb2 as sentinel_provider_v2_querier_pb2
import sentinel_protobuf.sentinel.provider.v2.querier_pb2_grpc as sentinel_provider_v2_querier_pb2_grpc


class ProviderQuerier:
    def __init__(self, channel: grpc._channel.Channel):
        self.__channel = channel
        self.__stub = sentinel_provider_v2_querier_pb2_grpc.QueryServiceStub(
            self.__channel
        )

    def QueryProvider(self, address: str) -> Any:
        try:
            r = self.__stub.QueryProvider(
                sentinel_provider_v2_querier_pb2.QueryProviderRequest(address=address)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.provider

    def QueryProviders(self, status: int) -> list:
        fetched_providers = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryProviders(
                    sentinel_provider_v2_querier_pb2.QueryProvidersRequest(
                        status=status
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryProviders(
                    sentinel_provider_v2_querier_pb2.QueryProvidersRequest(
                        status=status, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for p in r.providers:
                fetched_providers.append(p)

        return fetched_providers
