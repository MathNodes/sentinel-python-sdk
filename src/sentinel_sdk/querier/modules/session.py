from typing import Any

import grpc
import sentinel_protobuf.sentinel.session.v2.querier_pb2 as sentinel_session_v2_querier_pb2
import sentinel_protobuf.sentinel.session.v2.querier_pb2_grpc as sentinel_session_v2_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest


class SessionQuerier(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_session_v2_querier_pb2_grpc.QueryServiceStub(channel)

    def QuerySession(self, session_id: int) -> Any:
        try:
            r = self.__stub.QuerySession(
                sentinel_session_v2_querier_pb2.QuerySessionRequest(id=session_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.session

    def QuerySessions(self, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessions,
            request=sentinel_session_v2_querier_pb2.QuerySessionsRequest,
            attribute="sessions",
            pagination=pagination,
        )

    def QuerySessionsForAccount(
        self, address: str, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForAccount,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForAccountRequest,
            attribute="sessions",
            address=address,
            pagination=pagination,
        )

    def QuerySessionsForAllocation(
        self, allocation_id: int, address: str, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForAllocation,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForAllocationRequest,
            attribute="sessions",
            id=allocation_id,
            address=address,
            pagination=pagination,
        )

    def QuerySessionsForNode(
        self, address: str, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForNode,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForNodeRequest,
            attribute="sessions",
            address=address,
            pagination=pagination,
        )

    def QuerySessionsForSubscription(
        self, subscription_id: int, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForSubscription,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForSubscriptionRequest,
            attribute="sessions",
            id=subscription_id,
            pagination=pagination,
        )
