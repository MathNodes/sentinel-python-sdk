from typing import Any

import grpc
import sentinel_protobuf.sentinel.session.v2.querier_pb2 as sentinel_session_v2_querier_pb2
import sentinel_protobuf.sentinel.session.v2.querier_pb2_grpc as sentinel_session_v2_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier


class SessionQuerier(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_session_v2_querier_pb2_grpc.QueryServiceStub(channel)

    def QuerySession(self, sess_id: int) -> Any:
        try:
            r = self.__stub.QuerySession(
                sentinel_session_v2_querier_pb2.QuerySessionRequest(id=sess_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.session

    def QuerySessions(self) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessions,
            request=sentinel_session_v2_querier_pb2.QuerySessionsRequest,
            attribute="sessions",
        )

    def QuerySessionsForAccount(self, address: str) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForAccount,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForAccountRequest,
            attribute="sessions",
            args={"address": address},
        )

    def QuerySessionsForAllocation(self, address: str, allocation_id: int) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForAllocation,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForAllocationRequest,
            attribute="sessions",
            args={"address": address, "id": allocation_id},
        )

    def QuerySessionsForNode(self, address: str) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForNode,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForNodeRequest,
            attribute="sessions",
            args={"address": address},
        )

    def QuerySessionsForSubscription(self, subscription_id: int) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForSubscription,
            request=sentinel_session_v2_querier_pb2.QuerySessionsForSubscriptionRequest,
            attribute="sessions",
            args={"id": subscription_id},
        )
