import grpc

import sentinel_protobuf.cosmos.base.reflection.v1beta1.reflection_pb2 as cosmos_reflection_v1beta1_reflection_pb2
import sentinel_protobuf.cosmos.auth.v1beta1.auth_pb2 as cosmos_auth_v1beta1_auth_pb2
import sentinel_protobuf.cosmos.auth.v1beta1.query_pb2 as cosmos_auth_v1beta1_query_pb2

from sentinel_sdk.modules.deposit import DepositModule
from sentinel_sdk.modules.node import NodeModule
from sentinel_sdk.modules.plan import PlanModule
from sentinel_sdk.modules.swap import SwapModule
from sentinel_sdk.modules.provider import ProviderModule
from sentinel_sdk.modules.session import SessionModule
from sentinel_sdk.modules.subscription import SubscriptionModule

from mospy import Account
from mospy.clients import GRPCClient


from bip_utils import Bech32Encoder, Bip39SeedGenerator, Bip44, Bip44Coins, Bip39MnemonicValidator

from Crypto.Hash import RIPEMD160, SHA256

class SDKInstance:
    def __init__(self, grpcaddr: str, grpcport: int, secret: str = None, ssl: bool = False):
        try:
            self.__create_and_verify_channel(grpcaddr, grpcport, ssl=ssl)
        except grpc._channel._InactiveRpcError:
            raise ConnectionError("gRPC endpoint is invalid or not responding")

        self._client = None
        self._account = None

        if secret is not None:
            self.__setup_account_and_client(grpcaddr, grpcport, secret, ssl)

        self.__load_modules()


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
        self._channel = channel

    def __setup_account_and_client(self, grpcaddr: str, grpcport: int, secret: str, use_ssl: bool = False):
        self._account = self.__create_account(secret)
        self._client = self.__create_client(grpcaddr, grpcport, use_ssl)
        self._client.load_account_data(account=self._account)

    def __create_account(self, secret: str):
        try:
            Bip39MnemonicValidator().Validate(secret)
            seed_bytes = Bip39SeedGenerator(secret).Generate()
            bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()
        except:
            try:
                int(secret, 16)
                bip44_def_ctx = Bip44.FromPrivateKey(bytes.fromhex(secret), Bip44Coins.COSMOS)
            except:
                raise ValueError("Unrecognized secret either as a mnemonic or hex private key")

        sha_key = SHA256.new()
        ripemd_key = RIPEMD160.new()
        sha_key.update(bip44_def_ctx.PublicKey().RawCompressed().m_data_bytes)
        ripemd_key.update(sha_key.digest())
        bech32_pub = Bech32Encoder.Encode("sent", ripemd_key.digest())
        account_num = self.__get_account_number(bech32_pub)
        account = Account(
            private_key=bip44_def_ctx.PrivateKey().Raw().ToHex(),
            hrp="sent",
            account_number=account_num,
            protobuf="sentinel",
        )
        return account

    def __create_client(self, grpcaddr: str, grpcport: int, use_ssl: bool = False):
        client = GRPCClient(
            host=grpcaddr, port=grpcport, ssl=use_ssl, protobuf="sentinel"
        )
        return client

    def __get_account_number(self, address: str):
        tmp_stub = self._channel.unary_unary(
            "/cosmos.auth.v1beta1.Query/Account",
            request_serializer=cosmos_auth_v1beta1_query_pb2.QueryAccountRequest.SerializeToString,
            response_deserializer=cosmos_auth_v1beta1_query_pb2.QueryAccountResponse.FromString,
        )
        r = tmp_stub(cosmos_auth_v1beta1_query_pb2.QueryAccountRequest(address=address))
        baseacc = cosmos_auth_v1beta1_auth_pb2.BaseAccount()
        baseacc.ParseFromString(r.account.value)
        return baseacc.account_number


    def __load_modules(self):
        self.nodes = NodeModule(self._channel, 10, self._account, self._client)
        self.deposits = DepositModule(self._channel)
        self.plans = PlanModule(self._channel, self._account, self._client)
        self.providers = ProviderModule(self._channel, self._account, self._client)
        self.sessions = SessionModule(self._channel, self._account, self._client)
        self.subscriptions = SubscriptionModule(self._channel, self._account, self._client)
        self.swaps = SwapModule(self._channel, self._account, self._client)

    def renew_account(self, secret: str):
        self._account = self.__create_account(secret)
        self._client.load_account_data(account=self._account)
        self.__load_modules()

    def renew_grpc(self, grpcaddr: str, grpcport: int, use_ssl: bool = False):
        self._client = self.__create_client(grpcaddr, grpcport)
        self._client.load_account_data(account=self._account)
        self.__load_modules()
        
    @property
    def grpcaddr(self):
        return self._client._host
        
    @property
    def grpcport(self):
        return self._client._port

        
