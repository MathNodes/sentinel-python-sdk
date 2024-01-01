import base64
import hashlib
import json
import os
import ssl
import time
import urllib.parse
import urllib.request
import uuid
from typing import Any

import ecdsa
import grpc
import sentinel_protobuf.cosmos.auth.v1beta1.auth_pb2 as cosmos_auth_v1beta1_auth_pb2
import sentinel_protobuf.cosmos.auth.v1beta1.query_pb2 as cosmos_auth_v1beta1_query_pb2
from bip_utils import Bech32Encoder, Bip39SeedGenerator, Bip44, Bip44Coins
from Crypto.Hash import RIPEMD160, SHA256
from mospy import Account, Transaction
from mospy.clients import GRPCClient
from python_wireguard import Key
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from sentinel_protobuf.sentinel.node.v2.msg_pb2 import MsgSubscribeRequest
from sentinel_protobuf.sentinel.session.v2.msg_pb2 import MsgEndRequest, MsgStartRequest

from sentinel_sdk.types import NodeType


class SentinelTransactor:
    def __init__(
        self,
        grpcaddr: str,
        grpcport: int,
        query_channel: grpc.Channel,
        use_ssl: bool = False,
    ):
        self._query_channel = query_channel
        self.seed_path = os.path.join(os.getcwd(), "test.seed")
        if os.path.isfile(self.seed_path) is True:
            with open(self.seed_path, "r", encoding="utf-8") as f:
                mnemonic = f.read()
            self.__setup_account_and_client(mnemonic, grpcaddr, grpcport, use_ssl)
        else:
            print(f"{self.seed_path} file not found")

    def __setup_account_and_client(
        self, secret: str, grpcaddr: str, grpcport: int, use_ssl: bool = False
    ):
        # From mnemonic to pvt key using Bip, we could use directly Account(seed_phrase=)
        # But we would calculate the account_number dinamcally :)
        
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

        self.__account = Account(
            private_key=bip44_def_ctx.PrivateKey().Raw().ToHex(),
            hrp="sent",
            account_number=account_num,
            protobuf="sentinel",
        )
        self.__client = GRPCClient(
            host=grpcaddr, port=grpcport, ssl=use_ssl, protobuf="sentinel"
        )
        self.__client.load_account_data(account=self.__account)

    def __get_account_number(self, address: str):
        tmp_stub = self._query_channel.unary_unary(
            "/cosmos.auth.v1beta1.Query/Account",
            request_serializer=cosmos_auth_v1beta1_query_pb2.QueryAccountRequest.SerializeToString,
            response_deserializer=cosmos_auth_v1beta1_query_pb2.QueryAccountResponse.FromString,
        )
        r = tmp_stub(cosmos_auth_v1beta1_query_pb2.QueryAccountRequest(address=address))
        baseacc = cosmos_auth_v1beta1_auth_pb2.BaseAccount()
        baseacc.ParseFromString(r.account.value)
        return baseacc.account_number

    # TODO: subscribe_to_gigabytes, subscribe_to_hours, start_request and all method should have fee denom and amount as args?
    # We need to find a good way to this. **The method could return only the MsgRequest and type_url**
    # Who wants to submit the tx, can call transaction (we should also implement multi-add_raw_msg), one tx with multiple msg

    def subscribe_to_gigabytes(self, node_address: str, gigabytes: int):
        msg = MsgSubscribeRequest(
            frm=self.__account.address,
            node_address=node_address,
            gigabytes=gigabytes,
            hours=0,
            denom="udvpn",
        )
        return self.transaction([msg])

    def subscribe_to_hours(self, node_address: str, hours: int):
        msg = MsgSubscribeRequest(
            frm=self.__account.address,
            node_address=node_address,
            gigabytes=0,
            hours=hours,
            denom="udvpn",
        )
        return self.transaction([msg])

    def start_request(self, subscription_id: int, node_address: str):
        msg = MsgStartRequest(
            frm=self.__account.address, id=int(subscription_id), address=node_address
        )
        return self.transaction([msg])

    def end_request(self, session_id: int, rating: int = 0):
        msg = MsgEndRequest(
            frm=self.__account.address, id=int(session_id), rating=rating
        )
        return self.transaction([msg])

    def transaction(
        self,
        messages: list,
        fee_denom: str = "udvpn",
        fee_amount: int = 20000,
        gas: float = 0,
        gas_multiplier: float = 1.5,
    ) -> dict:
        tx = Transaction(
            account=self.__account,
            fee=Coin(denom=fee_denom, amount=f"{fee_amount}"),
            gas=gas,
            protobuf="sentinel",
            chain_id="sentinelhub-2",
        )

        if not isinstance(messages, list):
            messages = [messages]

        for message in messages:
            tx.add_raw_msg(message, type_url=f"/{message.DESCRIPTOR.full_name}")

        # inplace, auto-update gas with update=True
        # auto calculate the gas only if was not already passed as args:
        if gas == 0:
            self.__client.estimate_gas(
                transaction=tx, update=True, multiplier=gas_multiplier
            )

        tx_response = self.__client.broadcast_transaction(transaction=tx)
        # tx_response = {"hash": hash, "code": code, "log": log}
        return tx_response

    def wait_transaction(
        self, tx_hash: str, timeout: float = 60, pool_period: float = 60
    ):
        start = time.time()
        while 1:
            try:
                return self.__client.get_tx(tx_hash)
            except grpc.RpcError as rpc_error:
                # https://github.com/grpc/grpc/tree/master/examples/python/errors
                # Instance of 'RpcError' has no 'code' member, work on runtime
                status_code = rpc_error.code()  # pylint: disable=no-member
                if status_code == grpc.StatusCode.NOT_FOUND:
                    if time.time() - start > timeout:
                        return None
                    time.sleep(pool_period)

    # This can be also move, but can stay here because we access to self.__account.address
    def post_session(
        self, session_id: int, remote_url: str, node_type: NodeType = NodeType.WIREGUARD
    ):
        if node_type == NodeType.WIREGUARD:
            # [from golang] wgPrivateKey, err = wireguardtypes.NewPrivateKey()
            # [from golang] key = wgPrivateKey.Public().String()
            _, key = Key.key_pair()
        else:  # NodeType.V2RAY
            # os.urandom(16)
            # [from golang] uid, err = uuid.GenerateRandomBytes(16)
            # [from golang] key = base64.StdEncoding.EncodeToString(append([]byte{0x01}, uid...))
            key = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")

        # append([]byte{0x01}, uid) is required)
        # The key of wireguard is 32 bytes length, for v2ray only 16?

        sk = ecdsa.SigningKey.from_string(
            self.__account.private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256
        )

        session_id = int(session_id)
        # Uint64ToBigEndian
        bige_session = session_id.to_bytes(8, "big")
        signature = sk.sign(bige_session)

        payload = {
            "key": f"{key}",
            "signature": base64.b64encode(signature).decode("utf-8"),
        }
        return SentinelTransactor.post_session_node(
            f"{remote_url}/accounts/{self.__account.address}/sessions/{session_id}",
            payload,
        )

    # TODO: the following method was implement but should me moved out of "transactor"
    @staticmethod
    def search_attribute(tx_response: Any, event_type: str, attribute_key: str) -> Any:
        for event in (tx_response.tx_response or tx_response).events:
            if event.type == event_type:
                for attribute in event.attributes:
                    if attribute.key == attribute_key.encode():
                        return json.loads(attribute.value)
        return None

    # TODO: same as search_attribute, maybe we can do a utils file
    @staticmethod
    def post_session_node(url: str, payload: dict) -> dict:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        request = urllib.request.Request(url)
        request.add_header("Content-Type", "application/json; charset=utf-8")
        json_data_bytes = json.dumps(payload).encode("utf-8")  # needs to be bytes
        request.add_header("Content-Length", len(json_data_bytes))
        # TODO: status code != 200 was not handled
        with urllib.request.urlopen(
            request, json_data_bytes, timeout=(60 * 60), context=ctx
        ) as f:
            return json.loads(f.read().decode("utf-8"))
