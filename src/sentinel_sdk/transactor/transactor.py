import os

import sentinel_protobuf.cosmos.auth.v1beta1.auth_pb2 as cosmos_auth_v1beta1_auth_pb2
import sentinel_protobuf.cosmos.auth.v1beta1.query_pb2 as cosmos_auth_v1beta1_query_pb2
from bip_utils import Bech32Encoder, Bip39SeedGenerator, Bip44, Bip44Coins
from Crypto.Hash import RIPEMD160, SHA256
from mospy import Account, Transaction
from mospy.clients import GRPCClient
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from sentinel_protobuf.sentinel.node.v2.msg_pb2 import MsgSubscribeRequest


class SentinelTransactor:
    def __init__(self, grpcaddr, grpcport, query_channel):
        self._query_channel = query_channel
        self.seed_path = os.path.join(os.getcwd(), "test.seed")
        if os.path.isfile(self.seed_path) is True:
            with open(self.seed_path, "r") as f:
                mnemonic = f.read()
            self.__setup_account_and_client(mnemonic, grpcaddr, grpcport)
        else:
            print(f"{self.seed_path} file not found")

    def __setup_account_and_client(self, mnemonic, grpcaddr, grpcport):
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip44_def_ctx = Bip44.FromSeed(
            seed_bytes, Bip44Coins.COSMOS
        ).DeriveDefaultPath()
        sha_key = SHA256.new()
        ripemd_key = RIPEMD160.new()
        sha_key.update(bip44_def_ctx.PublicKey().RawCompressed().m_data_bytes)
        ripemd_key.update(sha_key.digest())
        bech32_pub = Bech32Encoder.Encode("sent", ripemd_key.digest())
        account_num = self.__get_account_number(bech32_pub)

        self.__account = Account(
            private_key=bip44_def_ctx.PrivateKey().Raw().ToHex(),
            hrp="sent",
            account_number=account_num,
            protobuf="sentinel",
        )
        self.__client = GRPCClient(
            host=grpcaddr, port=grpcport, ssl=False, protobuf="sentinel"
        )
        self.__client.load_account_data(account=self.__account)

    def __get_account_number(self, address):
        tmp_stub = self._query_channel.unary_unary(
            "/cosmos.auth.v1beta1.Query/Account",
            request_serializer=cosmos_auth_v1beta1_query_pb2.QueryAccountRequest.SerializeToString,
            response_deserializer=cosmos_auth_v1beta1_query_pb2.QueryAccountResponse.FromString,
        )
        r = tmp_stub(cosmos_auth_v1beta1_query_pb2.QueryAccountRequest(address=address))
        baseacc = cosmos_auth_v1beta1_auth_pb2.BaseAccount()
        baseacc.ParseFromString(r.account.value)
        return baseacc.account_number

    def SubscribeToGB(self, sentnode, gb):
        fee = Coin(denom="udvpn", amount="20000")
        tx = Transaction(
            account=self.__account,
            fee=fee,
            gas=0,
            protobuf="sentinel",
            chain_id="sentinelhub-2",
        )
        msg = MsgSubscribeRequest(
            frm=self.__account.address,
            node_address=sentnode,
            gigabytes=gb,
            hours=0,
            denom="udvpn",
        )
        tx.add_raw_msg(msg, type_url="/sentinel.node.v2.MsgSubscribeRequest")
        self.__client.estimate_gas(transaction=tx, update=True, multiplier=1.5)
        tx_response = self.__client.broadcast_transaction(transaction=tx)
        return tx_response
