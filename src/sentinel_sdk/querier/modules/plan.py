import sentinel_protobuf.sentinel.plan.v2.querier_pb2 as sentinel_plan_v2_querier_pb2
import sentinel_protobuf.sentinel.plan.v2.querier_pb2_grpc as sentinel_plan_v2_querier_pb2_grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import grpc

class PlanQuerier:
    def __init__(self, channel):
        self.__channel = channel
        self.__stub = sentinel_plan_v2_querier_pb2_grpc.QueryServiceStub(self.__channel)

    def QueryPlan(self, plan_id: int):
        try:
            r = self.__stub.QueryPlan(sentinel_plan_v2_querier_pb2.QueryPlanRequest(id=plan_id))
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.plan

    def QueryPlansForProvider(self, address: str, statusEnum: int):
        fetched_plans = []
        next_key = 0x01

        while(next_key):
            if(next_key == 0x01):
                r = self.__stub.QueryPlansForProvider(sentinel_plan_v2_querier_pb2.QueryPlansForProviderRequest(address=address, status=statusEnum))
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPlansForProvider(sentinel_plan_v2_querier_pb2.QueryPlansForProviderRequest(address=address, status=statusEnum, pagination=next_page_req))

            next_key = r.pagination.next_key
            for p in r.plans:
                fetched_plans.append(p)

        return fetched_plans

    def QueryPlans(self, statusEnum: int):
        fetched_plans = []
        next_key = 0x01

        while(next_key):
            if(next_key == 0x01):
                r = self.__stub.QueryPlans(sentinel_plan_v2_querier_pb2.QueryPlansRequest(status=statusEnum))
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPlans(sentinel_plan_v2_querier_pb2.QueryPlansRequest(status=statusEnum, pagination=next_page_req))

            next_key = r.pagination.next_key
            for p in r.plans:
                fetched_plans.append(p)

        return fetched_plans