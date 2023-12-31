from typing import Any

import grpc
import sentinel_protobuf.sentinel.subscription.v2.querier_pb2 as sentinel_subscription_v2_querier_pb2
import sentinel_protobuf.sentinel.subscription.v2.querier_pb2_grpc as sentinel_subscription_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.subscription.v2.subscription_pb2 as subscription_pb2

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.types import PageRequest


class SubscriptionQuerier(Querier):
    def __init__(self, channel: grpc.Channel):
        self.__stub = sentinel_subscription_v2_querier_pb2_grpc.QueryServiceStub(
            channel
        )

    def QuerySubscription(self, subscription_id: int) -> Any:
        try:
            r = self.__stub.QuerySubscription(
                sentinel_subscription_v2_querier_pb2.QuerySubscriptionRequest(
                    id=subscription_id
                )
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return self.__ConvertAnyToNodeSubscription(r.subscription.value)

    def QuerySubscriptions(self, pagination: PageRequest = None) -> list:
        subscriptions = self.QueryAll(
            query=self.__stub.QuerySubscriptions,
            request=sentinel_subscription_v2_querier_pb2.QuerySubscriptionsRequest,
            attribute="subscriptions",
            pagination=pagination,
        )
        return [
            self.__ConvertAnyToNodeSubscription(subscription.value)
            for subscription in subscriptions
        ]

    def QueryAllocation(self, address: str, subscription_id: int) -> list:
        try:
            r = self.__stub.QueryAllocation(
                sentinel_subscription_v2_querier_pb2.QueryAllocationRequest(
                    address=address, id=subscription_id
                )
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.allocation

    def QueryAllocations(
        self, subscription_id: int, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QueryAllocations,
            request=sentinel_subscription_v2_querier_pb2.QueryAllocationsRequest,
            attribute="allocations",
            id=subscription_id,
            pagination=pagination,
        )

    def QueryPayout(self, payout_id: int) -> Any:
        try:
            r = self.__stub.QueryPayout(
                sentinel_subscription_v2_querier_pb2.QueryPayoutRequest(id=payout_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.payout

    def QueryPayouts(self, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QueryPayouts,
            request=sentinel_subscription_v2_querier_pb2.QueryPayoutsRequest,
            attribute="payouts",
            pagination=pagination,
        )

    def QueryPayoutsForAccount(
        self, address: str, pagination: PageRequest = None
    ) -> list:
        return self.QueryAll(
            query=self.__stub.QueryPayoutsForAccount,
            request=sentinel_subscription_v2_querier_pb2.QueryPayoutsForAccountRequest,
            attribute="payouts",
            address=address,
            pagination=pagination,
        )

    def QueryPayoutsForNode(self, address: str, pagination: PageRequest = None) -> list:
        return self.QueryAll(
            query=self.__stub.QueryPayoutsForNode,
            request=sentinel_subscription_v2_querier_pb2.QueryPayoutsForNodeRequest,
            attribute="payouts",
            address=address,
            pagination=pagination,
        )

    def QuerySubscriptionsForAccount(
        self, address: str, pagination: PageRequest = None
    ) -> list:
        subscriptions = self.QueryAll(
            query=self.__stub.QuerySubscriptionsForAccount,
            request=sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForAccountRequest,
            attribute="subscriptions",
            address=address,
            pagination=pagination,
        )
        return [
            self.__ConvertAnyToPlanSubscription(subscription.value)
            for subscription in subscriptions
        ]

    def QuerySubscriptionsForNode(
        self, address: str, pagination: PageRequest = None
    ) -> list:
        subscriptions = self.QueryAll(
            query=self.__stub.QuerySubscriptionsForNode,
            request=sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForNodeRequest,
            attribute="subscriptions",
            address=address,
            pagination=pagination,
        )
        return [
            self.__ConvertAnyToNodeSubscription(subscription.value)
            for subscription in subscriptions
        ]

    def QuerySubscriptionsForPlan(
        self, plan_id: int, pagination: PageRequest = None
    ) -> list:
        subscriptions = self.QueryAll(
            query=self.__stub.QuerySubscriptionsForPlan,
            request=sentinel_subscription_v2_querier_pb2.QuerySubscriptionsForPlanRequest,
            attribute="subscriptions",
            id=plan_id,
            pagination=pagination,
        )
        return [
            self.__ConvertAnyToPlanSubscription(subscription.value)
            for subscription in subscriptions
        ]

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
