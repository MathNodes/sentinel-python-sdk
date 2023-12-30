from typing import Any

import grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import sentinel_protobuf.sentinel.plan.v2.querier_pb2 as sentinel_plan_v2_querier_pb2
import sentinel_protobuf.sentinel.plan.v2.querier_pb2_grpc as sentinel_plan_v2_querier_pb2_grpc


class PlanQuerier:
    def __init__(self, channel: grpc.Channel):
        self.__channel = channel
        self.__stub = sentinel_plan_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)

    def QueryPlan(self, plan_id: int) -> Any:
        try:
            r = self.__stub.QueryPlan(
                sentinel_plan_v2_querier_pb2.QueryPlanRequest(id=plan_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.plan

    def QueryPlansForProvider(self, address: str, status: int) -> list:
        fetched_plans = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryPlansForProvider(
                    sentinel_plan_v2_querier_pb2.QueryPlansForProviderRequest(
                        address=address, status=status.value
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPlansForProvider(
                    sentinel_plan_v2_querier_pb2.QueryPlansForProviderRequest(
                        address=address, status=status.value, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for p in r.plans:
                fetched_plans.append(p)

        return fetched_plans

    def QueryPlans(self, status: int) -> list:
        fetched_plans = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryPlans(
                    sentinel_plan_v2_querier_pb2.QueryPlansRequest(status=status.value)
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPlans(
                    sentinel_plan_v2_querier_pb2.QueryPlansRequest(
                        status=status.value, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for p in r.plans:
                fetched_plans.append(p)

        return fetched_plans
