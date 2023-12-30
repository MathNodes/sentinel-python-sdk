import grpc
import sentinel_protobuf.cosmos.base.reflection.v1beta1.reflection_pb2 as cosmos_reflection_v1beta1_reflection_pb2

from sentinel_sdk.querier.multiquerier import SentinelQuerier
from sentinel_sdk.transactor.transactor import SentinelTransactor


class SDKInstance:
    def __init__(self, grpcaddr: str, grpcport: int, ssl: bool = False):
        try:
            channel = self.__create_and_verify_channel(grpcaddr, grpcport, ssl=ssl)
        except grpc._channel._InactiveRpcError:
            raise ConnectionError("gRPC endpoint is invalid or not responding")

        self.multiquerier = SentinelQuerier(channel)
        self.transactor = SentinelTransactor(grpcaddr, grpcport, channel)

    def __create_and_verify_channel(
        self, grpcaddr: str, grpcport: int, ssl: bool = False
    ) -> grpc.Channel:
        channel = (
            grpc.secure_channel(
                f"{grpcaddr}:{grpcport}", credentials=grpc.ssl_channel_credentials()
            )
            if ssl is True
            else grpc.insecure_channel(f"{grpcaddr}:{grpcport}")
        )

        tmp_stub = channel.unary_unary(
            "/cosmos.base.reflection.v1beta1.ReflectionService/ListAllInterfaces",
            request_serializer=cosmos_reflection_v1beta1_reflection_pb2.ListAllInterfacesRequest.SerializeToString,
            response_deserializer=cosmos_reflection_v1beta1_reflection_pb2.ListAllInterfacesResponse.FromString,
        )

        # Test if the grpc is valid and respond to ListAllInterfacesRequest
        tmp_stub(cosmos_reflection_v1beta1_reflection_pb2.ListAllInterfacesRequest())
        return channel
