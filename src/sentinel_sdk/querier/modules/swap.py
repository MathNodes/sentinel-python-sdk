import sentinel_protobuf.sentinel.swap.v1.querier_pb2 as sentinel_swap_v1_querier_pb2
import sentinel_protobuf.sentinel.swap.v1.swap_pb2 as swap_pb2
import sentinel_protobuf.sentinel.swap.v1.querier_pb2_grpc as sentinel_swap_v1_querier_pb2_grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import grpc

class SwapQuerier:
    def __init__(self, channel):
        self.__channel = channel
        self.__stub = sentinel_swap_v1_querier_pb2_grpc.QueryServiceStub(self.__channel)

    def QuerySwap(self, tx_hash: bytes):
        try:
            r = self.__stub.QuerySwap(sentinel_swap_v1_querier_pb2.QuerySwapRequest(tx_hash = tx_hash))
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.swap

    def QuerySwaps(self):
        fetched_swaps = []
        next_key = 0x01

        while(next_key):
            if(next_key == 0x01):
                r = self.__stub.QuerySwaps(sentinel_swap_v1_querier_pb2.QuerySwapsRequest())
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySwaps(sentinel_swap_v1_querier_pb2.QuerySwapsRequest(pagination=next_page_req))

            next_key = r.pagination.next_key
            for s in r.swaps:
                fetched_swaps.append(s)

        return fetched_swaps