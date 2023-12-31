from typing import Any

import grpc
import sentinel_protobuf.sentinel.plan.v2.querier_pb2 as sentinel_plan_v2_querier_pb2
import sentinel_protobuf.sentinel.plan.v2.querier_pb2_grpc as sentinel_plan_v2_querier_pb2_grpc

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest


class PlanQuerier(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_plan_v2_querier_pb2_grpc.QueryServiceStub(channel)

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
