import grpc
import json
import sentinel_protobuf.cosmos.base.reflection.v1beta1.reflection_pb2 as cosmos_v1beta1_reflection_pb2 
from sentinel_sdk.querier.multiquerier import SentinelQuerier

class SDKInstance:
    def __init__(self, grpcaddr):
        try:
            self._channel = self.__create_and_verify_channel(grpcaddr)
        except grpc._channel._InactiveRpcError:
            raise ConnectionError("gRPC endpoint is invalid or not responding")

        self.multiquerier = SentinelQuerier(self._channel)
    
    def __create_and_verify_channel(self, grpcaddr):
        c = grpc.insecure_channel(grpcaddr)
        tmp_stub = c.unary_unary('/cosmos.base.reflection.v1beta1.ReflectionService/ListAllInterfaces', request_serializer=cosmos_v1beta1_reflection_pb2.ListAllInterfacesRequest.SerializeToString, response_deserializer=cosmos_v1beta1_reflection_pb2.ListAllInterfacesResponse.FromString)
        r = tmp_stub(cosmos_v1beta1_reflection_pb2.ListAllInterfacesRequest())
        return c