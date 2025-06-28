# Tkd-Alex
# Python implementation of: https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go

"""
# Too much issue with cosmpy and sentinel_protobuf / goproto import duplicated
from cosmpy.aerial.tx import Transaction
from cosmpy.aerial.tx_helpers import TxResponse
from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction
from cosmpy.aerial.client import LedgerClient, NetworkConfig

cfg = NetworkConfig(
    chain_id="sentinelhub-2",
    url="grpc+http://aimokoivunen.mathnodes.com:9090/",
    fee_minimum_gas_price=0.4,
    fee_denomination="udvpn",
    staking_denomination="udvpn",
)
client = LedgerClient(cfg)
"""

import base64
import hashlib
import json
import ssl
import urllib.parse
import urllib.request

import ecdsa
import grpc
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins

# pip install git+https://github.com/Tkd-Alex/mospy.git
from mospy import Account, Transaction
from mospy.clients import GRPCClient
from pywgkey import WgKey
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from sentinel_protobuf.sentinel.node.v2.msg_pb2 import MsgSubscribeRequest
from sentinel_protobuf.sentinel.node.v2.querier_pb2 import QueryNodeRequest
from sentinel_protobuf.sentinel.node.v2.querier_pb2_grpc import (
    QueryServiceStub as QueryNodeServiceStub,
)
from sentinel_protobuf.sentinel.session.v2.msg_pb2 import MsgStartRequest
from sentinel_protobuf.sentinel.session.v2.querier_pb2 import (
    QuerySessionsForAllocationRequest,
)
from sentinel_protobuf.sentinel.session.v2.querier_pb2_grpc import (
    QueryServiceStub as QuerySessionServiceStub,
)

# from mospy.clients import HTTPClient

# Custom version of mospy
# Tecnically we could re-implement mospy on this repository (https://github.com/MathNodes/sentinel-python-sdk)


def fetch_node_info(url: str) -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(f"{url}/status", timeout=(60 * 60), context=ctx) as f:
        return json.loads(f.read().decode("utf-8"))


def post_session_node(url: str, payload: dict) -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(url)
    request.add_header("Content-Type", "application/json; charset=utf-8")
    json_data_bytes = json.dumps(payload).encode("utf-8")  # needs to be bytes
    request.add_header("Content-Length", len(json_data_bytes))
    with urllib.request.urlopen(
        request, json_data_bytes, timeout=(60 * 60), context=ctx
    ) as f:
        return json.loads(f.read().decode("utf-8"))


grpc_host = "grpc.sentinel.co"
grpc_port = 9090

node_address = "sentnode123456789abcdefghilmopqrts"

mnemonic = "dont share your secret"
seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()

account = Account(
    private_key=bip44_def_ctx.PrivateKey().Raw().ToHex(),
    hrp="sent",
    account_number="38997",
    protobuf="sentinel",
)

# Subscribe to node request
# client = HTTPClient(api="https://api.sentinel.mathnodes.com")
client = GRPCClient(host=grpc_host, port=grpc_port, ssl=False, protobuf="sentinel")
client.load_account_data(account=account)

fee = Coin(denom="udvpn", amount="20000")
tx = Transaction(
    account=account, fee=fee, gas=0, protobuf="sentinel", chain_id="sentinelhub-2"
)
wmsg = MsgSubscribeRequest(
    frm=account.address, node_address=node_address, gigabytes=1, hours=0, denom="udvpn"
)
tx.add_raw_msg(wmsg, type_url="/sentinel.node.v2.MsgSubscribeRequest")
client.estimate_gas(transaction=tx, update=True, multiplier=1.5)
tx_response = client.broadcast_transaction(transaction=tx)

"""
con = client._connect()
tx_stub = client._cosmos_tx_service_pb2_grpc.ServiceStub(con)
tx_response = tx_stub.GetTx(client._cosmos_tx_service_pb2.GetTxRequest(hash=tx_response["hash"]))
"""

"""
from sentinel_protobuf.cosmos.tx.v1beta1.service_pb2_grpc import ServiceStub
from sentinel_protobuf.cosmos.tx.v1beta1.service_pb2 import GetTxRequest
channel = grpc.insecure_channel(f"{grpc_host}:{grpc_port}")
stub = ServiceStub(con)
tx_response = stub.GetTx(GetTxRequest(hash=tx_response["hash"]))
"""

# Maybe wait the tx before query ...
tx_response = client.get_tx(tx_response["hash"])

# Looking for subscription_id (sentinel.node.v2.EventCreateSubscription)
# We can do better, for the moment just iterate over the events
subscription_id = None
for event in tx_response.tx_response.events:
    if event.type == "sentinel.node.v2.EventCreateSubscription":
        for attribute in event.attributes:
            if attribute.key == b"id":
                # Why the hell the values are encoded grrr
                subscription_id = json.loads(attribute.value)
        break


channel = grpc.insecure_channel(f"{grpc_host}:{grpc_port}")

# Query node
# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L192-L197
# Please use the sdk here....


stub = QueryNodeServiceStub(channel)

response = stub.QueryNode(QueryNodeRequest(address=node_address))
remote_url = response.node.remote_url

# Fetch info, in order to determine node type V2Ray or Wireguard
# Currently on wireguard is implement in this script
# Btw, for V2Ray the key It's just a random uuid
# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L199-L202
node_info = fetch_node_info(remote_url)

# Query active session >> Sentinecli still user v1 query :/
# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L210-L213
# from sentinel_protobuf.sentinel.session.v1.querier_pb2 import QuerySessionsForAddressRequest
# from sentinel_protobuf.sentinel.session.v1.querier_pb2_grpc import QueryNodeServiceStub
# No querirer for v1 :(
# Please use the sdk here....


stub = QuerySessionServiceStub(channel)
response = stub.QuerySessionsForAllocation(
    QuerySessionsForAllocationRequest(id=int(subscription_id), address=account.address)
)

# If session already exist send NewMsgEndRequest
# Bypass for the moment ....
# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L215-L224

# Start new session NewMsgStartRequest
# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L225-L237

client = GRPCClient(host=grpc_host, port=grpc_port, ssl=False, protobuf="sentinel")
# load_account_data required for each new tx
client.load_account_data(account=account)

fee = Coin(denom="udvpn", amount="20000")
tx = Transaction(
    account=account, fee=fee, gas=0, protobuf="sentinel", chain_id="sentinelhub-2"
)
wmsg = MsgStartRequest(
    frm=account.address, id=int(subscription_id), address=node_address
)
tx.add_raw_msg(wmsg, type_url="/sentinel.session.v2.MsgStartRequest")
client.estimate_gas(transaction=tx, update=True, multiplier=1.5)
tx_response = client.broadcast_transaction(transaction=tx)
# Maybe wait the tx before query ...
tx_response = client.get_tx(tx_response["hash"])

# Looking for session_id (sentinel.node.v2.EventCreateSubscription)
# We can do better, for the moment just iterate over the events
session_id = None
for event in tx_response.tx_response.events:
    if event.type == "sentinel.session.v2.EventStart":
        for attribute in event.attributes:
            if attribute.key == b"id":
                # Why the hell the values are encoded grrr
                session_id = json.loads(attribute.value)
        break

# Query again active session, we should have the same of session_id
# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L239-L245
# Please use the sdk here....

stub = QuerySessionServiceStub(channel)
response = stub.QuerySessionsForAllocation(
    QuerySessionsForAllocationRequest(id=int(subscription_id), address=account.address)
)

for session in response.sessions:
    if session.subscription_id == int(subscription_id):
        if session.id == int(session_id):
            print("Session exist", session)
            break

# https://github.com/sentinel-official/cli-client/blob/master/cmd/connect.go#L253-L306
wgkey = WgKey()
private = wgkey.privkey
public = wgkey.pubkey

prv_key = bip44_def_ctx.PrivateKey().Raw().ToBytes()
sk = ecdsa.SigningKey.from_string(
    prv_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256
)

session_id = int(session_id)
# Uint64ToBigEndian
bige_session = session_id.to_bytes(8, "big")
signature = sk.sign(bige_session)

payload = {"key": f"{public}", "signature": base64.b64encode(signature).decode("utf-8")}

response = post_session_node(
    f"{remote_url}/accounts/{account.address}/sessions/{session_id}", payload
)
print(response)
