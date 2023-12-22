from sentinel_sdk.querier.modules.deposit import DepositQuerier
from sentinel_sdk.querier.modules.node import NodeQuerier
from sentinel_sdk.querier.modules.plan import PlanQuerier
from sentinel_sdk.querier.modules.provider import ProviderQuerier

class SentinelQuerier:
    def __init__(self, channel):
        self._channel = channel
        self.node_querier = NodeQuerier(self._channel, 10)
        self.deposit_querier = DepositQuerier(self._channel)
        self.plan_querier = PlanQuerier(self._channel)
        self.provider_querier = ProviderQuerier(self._channel)