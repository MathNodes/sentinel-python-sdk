from typing import Any

import grpc
import sentinel_protobuf.sentinel.session.v3.querier_pb2 as sentinel_session_v3_querier_pb2
import sentinel_protobuf.sentinel.session.v3.querier_pb2_grpc as sentinel_session_v3_querier_pb2_grpc
import sentinel_protobuf.sentinel.session.v3.msg_pb2 as msg_pb2

from google.protobuf.duration_pb2 import Duration

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams


class SessionModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, client):
        self.__stub = sentinel_session_v3_querier_pb2_grpc.QueryServiceStub(channel)
        self._account = account
        self._client = client

    def QuerySession(self, session_id: int) -> Any:
        try:
            r = self.__stub.QuerySession(
                sentinel_session_v3_querier_pb2.QuerySessionRequest(id=session_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.session

    def QuerySessions(self, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessions,
            request=sentinel_session_v3_querier_pb2.QuerySessionsRequest,
            attribute="sessions",
            pagination=pagination,
        )

    def QuerySessionsForAccount(
        self, address: str, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForAccount,
            request=sentinel_session_v3_querier_pb2.QuerySessionsForAccountRequest,
            attribute="sessions",
            address=address,
            pagination=pagination,
        )

    def QuerySessionsForAllocation(
        self, allocation_id: int, address: str, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForAllocation,
            request=sentinel_session_v3_querier_pb2.QuerySessionsForAllocationRequest,
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
            request=sentinel_session_v3_querier_pb2.QuerySessionsForNodeRequest,
            attribute="sessions",
            address=address,
            pagination=pagination,
        )

    def QuerySessionsForSubscription(
        self, subscription_id: int, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QuerySessionsForSubscription,
            request=sentinel_session_v3_querier_pb2.QuerySessionsForSubscriptionRequest,
            attribute="sessions",
            id=subscription_id,
            pagination=pagination,
        )

    def EndSession(self, session_id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgCancelSessionRequest(
            frm=self._account.address,
            id=session_id,
        )
        return self.transaction([msg], tx_params)

    def UpdateSession(
        self,
        session_id: int,
        download_bytes: int,
        upload_bytes: int,
        duration_seconds: int,
        signature: bytes,
        tx_params: TxParams = TxParams(),
    ):
        msg = msg_pb2.MsgUpdateSessionRequest(
            frm=self._account.address,
            id=session_id,
            download_bytes=str(download_bytes),
            upload_bytes=str(upload_bytes),
            duration=Duration(seconds=duration_seconds),
            signature=signature,
        )
        return self.transaction([msg], tx_params)

    def UpdateParams(self, params, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateParamsRequest(
            frm=self._account.address,
            params=params,
        )
        return self.transaction([msg], tx_params)
