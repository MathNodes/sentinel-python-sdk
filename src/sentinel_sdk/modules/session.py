from typing import Any

import grpc
import sentinel_protobuf.sentinel.session.v2.querier_pb2 as sentinel_session_v2_querier_pb2
import sentinel_protobuf.sentinel.session.v2.querier_pb2_grpc as sentinel_session_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.session.v2.msg_pb2 as msg_pb2

from sentinel_protobuf.sentinel.session.v2 import proof_pb2
from sentinel_protobuf.sentinel.types.v1.bandwidth_pb2 import Bandwidth
from google.protobuf.duration_pb2 import Duration

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams


class SessionModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, client):
        self.__stub = sentinel_session_v2_querier_pb2_grpc.QueryServiceStub(channel)
        self._account = account
        self._client = client

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

    def StartSession(self, address: str, subscription_id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgStartRequest(
            frm = self._account.address,
            id = subscription_id,
            address = address
        )
        return self.transaction([msg], tx_params)

    def EndSession(self, session_id: int, rating: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgEndRequest(
            frm = self._account.address,
            id = session_id,
            rating = rating,
        )
        return self.transaction([msg], tx_params)

    def UpdateDetails(self, proof: proof_pb2.Proof, signature: bytes, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateDetailsRequest(
            frm = self._account.address,
            proof = proof,
            signature = signature,
        )
        return self.transaction([msg], tx_params)

    def Proof(self, session_id: int, bandwidth: Bandwidth, duration: Duration) -> proof_pb2.Proof:
        return proof_pb2.Proof(
            id=session_id,
            bandwidth=bandwidth,
            duration=duration
        )