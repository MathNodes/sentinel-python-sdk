from typing import Any

import grpc
import sentinel_protobuf.sentinel.subscription.v2.querier_pb2 as sentinel_subscription_v2_querier_pb2
import sentinel_protobuf.sentinel.subscription.v2.querier_pb2_grpc as sentinel_subscription_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.subscription.v2.subscription_pb2 as subscription_pb2
import sentinel_protobuf.sentinel.subscription.v2.msg_pb2 as msg_pb2
import sentinel_protobuf.sentinel.subscription.v3.msg_pb2 as msg_pb2_3
from sentinel_protobuf.sentinel.types.v1.renewal_pb2 import RenewalPricePolicy

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams


class SubscriptionModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, client):
        self.__stub = sentinel_subscription_v2_querier_pb2_grpc.QueryServiceStub(
            channel
        )
        self._account = account
        self._client = client

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
            self.__ConvertAnyToNodeSubscription(subscription.value)
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
        
    # not in use anymore
    '''
    def Allocate(self, address: str, bytes: str, id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgAllocateRequest(
            frm = self._account.address,
            address = address,
            bytes = bytes,
            id = id,
        )
        return self.transaction([msg], tx_params)

    
    def Cancel(self, id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgCancelRequest(
            frm = self._account.address,
            id = id,
        )
        return self.transaction([msg], tx_params)
    '''
    
    # id is subscription id
    def Cancel(self, id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2_3.MsgCancelSubscriptionRequest(
            frm = self._account.address,
            id = id,
        )
        return self.transaction([msg], tx_params)
    
    def RenewSubscription(self, subscription_id: int, denom: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2_3.MsgRenewSubscriptionRequest(
            frm = self._account.address,
            id = subscription_id,
            denom = denom,
        )
        return self.transaction([msg], tx_params)
    
    def ShareSubscription(self, subscription_id: int, wallet_address: str, bytes: str, tx_params: TxParams = TxParams()):
        msg = msg_pb2_3.MsgShareSubscriptionRequest(
            frm = self._account.address,
            id = subscription_id,
            acc_address = wallet_address,
            bytes = bytes,
        )
        return self.transaction([msg], tx_params)
    
    # id is plan_id 
    def StartSubscription(self, plan_id: int, denom: str, renewal: int = RenewalPricePolicy.RENEWAL_PRICE_POLICY_IF_LESSER_OR_EQUAL, tx_params: TxParams = TxParams()):
        msg = msg_pb2_3.MsgStartSubscriptionRequest(
            frm = self._account.address,
            id = plan_id,
            denom = denom,
            renewal_price_polilcy = renewal,
        )
        return self.transaction([msg], tx_params)
    
    def UpdateSubscription(self, subscription_id: int,  renewal: int = RenewalPricePolicy.RENEWAL_PRICE_POLICY_IF_LESSER_OR_EQUAL, tx_params: TxParams = TxParams()):
        msg = msg_pb2_3.MsgUpdateSubscriptionRequest(
            frm = self._account.address,
            id = id,
            renewal_price_policy = renewal,
        )
        return self.transaction([msg], tx_params)
    
    # Used for plan subs        
    def StartSession(self, address: str, subscription_id: int, next_sequence: bool = False,  tx_params: TxParams = TxParams()):
        msg = msg_pb2_3.MsgStartSessionRequest(
            frm = self._account.address,
            id = subscription_id,
            node_address = address
        )
        return self.transaction([msg], tx_params, next_sequence)
    
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
