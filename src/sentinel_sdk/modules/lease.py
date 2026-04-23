
import grpc
import sentinel_protobuf.sentinel.lease.v1.lease_pb2 as lease_pb2
import sentinel_protobuf.sentinel.lease.v1.querier_pb2 as sentinel_subscription_v2_querier_pb2
import sentinel_protobuf.sentinel.lease.v1.querier_pb2_grpc as sentinel_subscription_v2_querier_pb2_grpc
import sentinel_protobuf.sentinel.subscription.v2.subscription_pb2 as subscription_pb2
import sentinel_protobuf.sentinel.lease.v1.msg_pb2 as msg_pb2
from sentinel_protobuf.sentinel.types.v1.price_pb2 import Price
from sentinel_protobuf.sentinel.types.v1.renewal_pb2 import RenewalPricePolicy

from sentinel_sdk.querier.querier import Querier
from sentinel_sdk.transactor.transactor import Transactor
from sentinel_sdk.types import PageRequest, TxParams

class LeaseModule(Querier, Transactor):
    def __init__(self, channel: grpc.Channel, account, provider_account, client):
        self.__stub = sentinel_subscription_v2_querier_pb2_grpc.QueryServiceStub(
            channel
        )
        self._account = account
        self._client = client
        self._provider_account = provider_account
        
    def EndLease(self, subscription_id: int, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgEndLeaseRequest(
            frm = self._provider_account.address,
            id = subscription_id,
        )
        
        return self.transaction([msg], tx_params)
    
    def RenewLease(self, subscription_id: int, hours: int, max_price: Price = Price, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgRenewLeaseRequest(
            frm = self._provider_account.address,
            id = subscription_id,
            hours = hours,
            max_price = max_price,
        )
        
        return self.transaction([msg], tx_params)
    
    def StartLease(self, node: str, hours: int, max_price: Price, renewal: int = RenewalPricePolicy.RENEWAL_PRICE_POLICY_IF_LESSER_OR_EQUAL, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgStartLeaseRequest(
            frm = self._provider_account.address,
            node_address = node,
            hours = hours,
            max_price = max_price,
            renewal_price_policy = renewal,
        )
        
        return self.transaction([msg], tx_params)
    
    def UpdateLease(self, subscription_id: int, renewal: int = RenewalPricePolicy.RENEWAL_PRICE_POLICY_IF_LESSER_OR_EQUAL, tx_params: TxParams = TxParams()):
        msg = msg_pb2.MsgUpdateLeaseRequest(
            frm = self._provider_account.address,
            id = subscription_id,
            renewal_price_policy = renewal,
        )
        
        return self.transaction([msg], tx_params)
    
    
    
    
    