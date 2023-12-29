import grpc
import json
import sentinel_protobuf.cosmos.base.reflection.v1beta1.reflection_pb2 as cosmos_reflection_v1beta1_reflection_pb2 

from sentinel_sdk.querier.multiquerier import SentinelQuerier
# from sentinel_sdk.transactor.transactor import SentinelTransactor


class SDKInstance:
    def __init__(self, grpcaddr, grpcport):
        try:
            channel = self.__create_and_verify_channel(grpcaddr, grpcport)
        except grpc._channel._InactiveRpcError:
            raise ConnectionError("gRPC endpoint is invalid or not responding")

        self.multiquerier = SentinelQuerier(channel)
        # self.transactor = SentinelTransactor(grpcaddr, grpcport, channel)
    

    def __create_and_verify_channel(self, grpcaddr, grpcport):
        c = grpc.insecure_channel(f"{grpcaddr}:{grpcport}")
        tmp_stub = c.unary_unary('/cosmos.base.reflection.v1beta1.ReflectionService/ListAllInterfaces', request_serializer=cosmos_reflection_v1beta1_reflection_pb2.ListAllInterfacesRequest.SerializeToString, response_deserializer=cosmos_reflection_v1beta1_reflection_pb2.ListAllInterfacesResponse.FromString)
        r = tmp_stub(cosmos_reflection_v1beta1_reflection_pb2.ListAllInterfacesRequest())
        return c


