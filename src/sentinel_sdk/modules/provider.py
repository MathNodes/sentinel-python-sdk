from typing import Any

import grpc
import sentinel_protobuf.sentinel.provider.v2.querier_pb2 as sentinel_provider_v2_querier_pb2
import sentinel_protobuf.sentinel.provider.v2.querier_pb2_grpc as sentinel_provider_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.provider.v2.msg_pb2 as msg_pb2

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams


class ProviderModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, client):
        self.__stub = sentinel_provider_v2_querier_pb2_grpc.QueryServiceStub(channel)
        self._account = account
        self._client = client

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

    def Register(self, description: str, identity: str, name: str, website: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgRegisterRequest(
            frm = self._account.address,
            description = description,
            identity = identity,
            name = name,
            website = website,
        )
        return self.transaction([msg], tx_params)

    def Update(self, description: str, identity: str, name: str, website: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateRequest(
            frm = self._account.address,
            description = description,
            identity = identity,
            name = name,
            website = website,
        )
        return self.transaction([msg], tx_params)