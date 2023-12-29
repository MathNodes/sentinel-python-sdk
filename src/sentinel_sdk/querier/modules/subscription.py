from typing import Any

import grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import sentinel_protobuf.sentinel.subscription.v2.querier_pb2 as sentinel_subscription_v2_querier_pb2
import sentinel_protobuf.sentinel.subscription.v2.querier_pb2_grpc as sentinel_subscription_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.subscription.v2.subscription_pb2 as subscription_pb2


class SubscriptionQuerier:
    def __init__(self, channel: grpc.Channel):
        self.__channel = channel
        self.__stub = sentinel_subscription_v2_querier_pb2_grpc.QueryServiceStub(
            self.__channel
        )

    def QuerySubscription(self, subscr_id: int) -> Any:
        try:
            r = self.__stub.QuerySubscription(
                sentinel_subscription_v2_querier_pb2.QuerySubscriptionRequest(
                    id=subscr_id
                )
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return self.__ConvertAnyToNodeSubscription(r.subscription.value)

    def QuerySubscriptions(self) -> list:
        fetched_subscriptions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySubscriptions(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsRequest()
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySubscriptions(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsRequest(
                        pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.subscriptions:
                fetched_subscriptions.append(
                    self.__ConvertAnyToNodeSubscription(s.value)
                )

        return fetched_subscriptions

    def QueryAllocation(self, address: str, alloc_id: int) -> list:
        try:
            r = self.__stub.QueryAllocation(
                sentinel_subscription_v2_querier_pb2.QueryAllocationRequest(
                    address=address, id=alloc_id
                )
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.allocation

    def QueryAllocations(self, alloc_id: int) -> list:
        fetched_allocations = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryAllocations(
                    sentinel_subscription_v2_querier_pb2.QueryAllocationsRequest(
                        id=alloc_id
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryAllocations(
                    sentinel_subscription_v2_querier_pb2.QueryAllocationsRequest(
                        id=alloc_id, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for a in r.allocations:
                fetched_allocations.append(a)

        return fetched_allocations

    def QueryPayout(self, payout_id: int) -> Any:
        try:
            r = self.__stub.QueryPayout(
                sentinel_subscription_v2_querier_pb2.QueryPayoutRequest(id=payout_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.payout

    def QueryPayouts(self) -> list:
        fetched_payouts = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryPayouts(
                    sentinel_subscription_v2_querier_pb2.QueryPayoutsRequest()
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPayouts(
                    sentinel_subscription_v2_querier_pb2.QueryPayoutsRequest(
                        pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for p in r.payouts:
                fetched_payouts.append(p)

        return fetched_payouts

    def QueryPayoutsForAccount(self, address: str) -> list:
        fetched_payouts = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryPayoutsForAccount(
                    sentinel_subscription_v2_querier_pb2.QueryPayoutsForAccountRequest(
                        address=address
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPayoutsForAccount(
                    sentinel_subscription_v2_querier_pb2.QueryPayoutsForAccountRequest(
                        address=address, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for p in r.payouts:
                fetched_payouts.append(p)

        return fetched_payouts

    def QueryPayoutsForNode(self, address: str) -> list:
        fetched_payouts = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QueryPayoutsForNode(
                    sentinel_subscription_v2_querier_pb2.QueryPayoutsForNodeRequest(
                        address=address
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryPayoutsForNode(
                    sentinel_subscription_v2_querier_pb2.QueryPayoutsForNodeRequest(
                        address=address, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for p in r.payouts:
                fetched_payouts.append(p)

        return fetched_payouts

    def QuerySubscriptionsForAccount(self, address: str) -> list:
        fetched_subscriptions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySubscriptionsForAccount(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForAccountRequest(
                        address=address
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySubscriptionsForAccount(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForAccountRequest(
                        address=address, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.subscriptions:
                fetched_subscriptions.append(
                    self.__ConvertAnyToPlanSubscription(s.value)
                )

        return fetched_subscriptions

    def QuerySubscriptionsForNode(self, address: str) -> list:
        fetched_subscriptions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySubscriptionsForNode(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForNodeRequest(
                        address=address
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySubscriptionsForNode(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForNodeRequest(
                        address=address, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.subscriptions:
                fetched_subscriptions.append(
                    self.__ConvertAnyToNodeSubscription(s.value)
                )

        return fetched_subscriptions

    def QuerySubscriptionsForPlan(self, plan_id: int) -> list:
        fetched_subscriptions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySubscriptionsForPlan(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForPlanRequest(
                        id=plan_id
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySubscriptionsForPlan(
                    sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForPlanRequest(
                        id=plan_id, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.subscriptions:
                fetched_subscriptions.append(
                    self.__ConvertAnyToPlanSubscription(s.value)
                )

        return fetched_subscriptions

    # Node subscriptions are returned by grpc querier in google's 'Any' type and need to be converted into desired protobuf type
    #
    #
    def __ConvertAnyToNodeSubscription(self, any_proto: bytes) -> Any:
        nodesub = subscription_pb2.NodeSubscription()
        nodesub.ParseFromString(any_proto)
        return nodesub

    def __ConvertAnyToPlanSubscription(self, any_proto: bytes) -> Any:
        plansub = subscription_pb2.PlanSubscription()
        plansub.ParseFromString(any_proto)
        return plansub
