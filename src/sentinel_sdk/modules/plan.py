from typing import Any

import grpc
import sentinel_protobuf.sentinel.plan.v2.querier_pb2 as sentinel_plan_v2_querier_pb2
import sentinel_protobuf.sentinel.plan.v2.querier_pb2_grpc as sentinel_plan_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.plan.v2.msg_pb2 as msg_pb2

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams


class PlanModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, client):
        self.__stub = sentinel_plan_v2_querier_pb2_grpc.QueryServiceStub(channel)
        self._account = account 
        self._client = client

    def QueryPlan(self, plan_id: int) -> Any:
        try:
            r = self.__stub.QueryPlan(
                sentinel_plan_v2_querier_pb2.QueryPlanRequest(id=plan_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.plan

    def QueryPlansForProvider(
        self, address: str, status: int, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QueryPlansForProvider,
            request=sentinel_plan_v2_querier_pb2.QueryPlansForProviderRequest,
            attribute="plans",
            address=address,
            status=status.value,
            pagination=pagination,
        )

    def QueryPlans(self, status: int, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QueryPlans,
            request=sentinel_plan_v2_querier_pb2.QueryPlansRequest,
            attribute="plans",
            status=status.value,
            pagination=pagination,
        )

    def Create(self, duration: int, gigabytes: int, prices: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgCreateRequest(
            frm = self._account.address,
            duration = duration,
            gigabytes = gigabytes,
            prices = prices,
        )
        return self.transaction([msg], tx_params)

    def LinkNode(self, plan_id: int, node_address: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgLinkNodeRequest(
            frm = self._account.address,
            id = plan_id,
            node_address = node_address,
        )
        return self.transaction([msg], tx_params)

    def Subscribe(self, denom: str, plan_id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgSubscribeRequest(
            frm = self._account.address,
            id = plan_id,
            denom = denom,
        )
        return self.transaction([msg], tx_params)

    def UnlinkNode(self, plan_id: int, node_address: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUnlinkNodeRequest(
            frm = self._account.address,
            id = plan_id,
            node_address = node_address,
        )
        return self.transaction([msg], tx_params)

    def UpdateStatus(self, plan_id: int, status: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateStatusRequest(
            frm = self._account.address,
            id = plan_id,
            status = status,
        )
        return self.transaction([msg], tx_params)
