import grpc
import json
from sentinel_sdk.querier.multiquerier import SentinelQuerier

class SentinelSDK:
    def __init__(self, grpcaddr):
        self._channel = grpc.insecure_channel(grpcaddr)
        self.multiquerier = SentinelQuerier(self._channel)
