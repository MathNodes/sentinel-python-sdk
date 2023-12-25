import sentinel_protobuf.sentinel.deposit.v1.querier_pb2 as sentinel_deposit_v1_querier_pb2
import sentinel_protobuf.sentinel.deposit.v1.querier_pb2_grpc as sentinel_deposit_v1_querier_pb2_grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import grpc

class DepositQuerier:
    def __init__(self, channel):
        self.__channel = channel
        self.__stub = sentinel_deposit_v1_querier_pb2_grpc.QueryServiceStub(self.__channel)

    def QueryDeposit(self, address: str):
        try:
            r = self.__stub.QueryDeposit(sentinel_deposit_v1_querier_pb2.QueryDepositRequest(address=address))
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.deposit

    def QueryDeposits(self):
        fetched_deposits = []
        next_key = 0x01

        while(next_key):
            if(next_key == 0x01):
                r = self.__stub.QueryDeposits(sentinel_deposit_v1_querier_pb2.QueryDepositsRequest())
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QueryDeposits(sentinel_deposit_v1_querier_pb2.QueryDepositsRequest(pagination=next_page_req))

            next_key = r.pagination.next_key
            for d in r.deposits:
                fetched_deposits.append(d)

        return fetched_deposits
