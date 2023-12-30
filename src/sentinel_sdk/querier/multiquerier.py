import grpc

from sentinel_sdk.querier.modules.deposit import DepositQuerier
from sentinel_sdk.querier.modules.node import NodeQuerier
from sentinel_sdk.querier.modules.plan import PlanQuerier
from sentinel_sdk.querier.modules.provider import ProviderQuerier
from sentinel_sdk.querier.modules.session import SessionQuerier
from sentinel_sdk.querier.modules.subscription import SubscriptionQuerier
from sentinel_sdk.querier.modules.swap import SwapQuerier


class SentinelQuerier:
    def __init__(self, channel: grpc.Channel):
        self._channel = channel
        self.node_querier = NodeQuerier(self._channel, 10)
        self.deposit_querier = DepositQuerier(self._channel)
        self.plan_querier = PlanQuerier(self._channel)
        self.provider_querier = ProviderQuerier(self._channel)
        self.session_querier = SessionQuerier(self._channel)
        self.subscription_querier = SubscriptionQuerier(self._channel)
        self.swap_querier = SwapQuerier(self._channel)
