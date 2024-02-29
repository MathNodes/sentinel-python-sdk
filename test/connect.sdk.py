import json

import grpc
from sentinel_protobuf.sentinel.node.v2.msg_pb2 import MsgSubscribeRequest
from sentinel_protobuf.sentinel.session.v2.msg_pb2 import MsgEndRequest, MsgStartRequest

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import NodeType, TxParams, Status
from sentinel_sdk.utils import search_attribute

# GRPC_VERBOSITY=debug GRPC_TRACE=tcp,http python test/queryall.py

# NEVER SHARE YOUR SECRET!
secret = input("your secret: ")

sdk = SDKInstance(grpcaddr="grpc.sentinel.co", grpcport=9090, secret=secret)

# The address can be founded in every modules because is inherited
# For example: sdk.sessions._account.address
print(sdk.nodes._account.address)

node_address = input("give a node address: ")
node = sdk.nodes.QueryNode(node_address)
node_status = json.loads(sdk.nodes.QueryNodeStatus(node))
assert node.address == node_address == node_status["result"]["address"]

try:
    # tx = sdk.transactor.subscribe_to_gigabytes(node_address=node_address, gigabytes=1)
    tx = sdk.nodes.SubscribeToNode(
        node_address=node_address,
        gigabytes=1,
        hours=0,
        denom="udvpn",  # Comment this, raise exception
        tx_params=TxParams(),
    )
except grpc.RpcError as rpc_error:
    # TODO: this should be handled on skd side
    print(rpc_error.code())  # pylint: disable=no-member
    print(rpc_error.details())  # pylint: disable=no-member
    print(rpc_error.debug_error_string())  # pylint: disable=no-member

# The wait_for_tx can be founded in every modules because is inherited
# For example: tx_response = sdk.sessions.wait_for_tx(tx["hash"])
tx_response = sdk.nodes.wait_for_tx(tx["hash"])

subscription_id = search_attribute(
    tx_response, "sentinel.node.v2.EventCreateSubscription", "id"
)

# Double verify the subscription
subscription = sdk.subscriptions.QuerySubscription(
    int(subscription_id)
)
assert (
    subscription.base.id == int(subscription_id)
    and subscription.node_address == node_address
)

sessions = sdk.sessions.QuerySessionsForSubscription(
    subscription.base.id
)

# TODO: return message instead of executing the tx It's currently not supported ...

"""
messages = []
if sessions != []:
    for session in sessions:
        messages.append(
            sdk.transactor.PrepareOrTransactMsg(
                MsgEndRequest, id=session.id, rating=0, transact=False
            )
        )

messages.append(
    sdk.transactor.PrepareOrTransactMsg(
        MsgStartRequest, id=int(subscription_id), address=node_address, transact=False
    )
)

# TODO: Currently doesn't work, we should call self.__client.load_account_data, before each tx
try:
    tx = sdk.transactor.transaction(messages, tx_params=TxParams())
    tx_response = sdk.transactor.wait_for_tx(tx["hash"])
except grpc.RpcError as rpc_error:
    # TODO: this should be handled on skd side
    print(rpc_error.code())  # pylint: disable=no-member
    print(rpc_error.details())  # pylint: disable=no-member
    print(rpc_error.debug_error_string())  # pylint: disable=no-member
"""

for session in sessions:
    if session.status == Status.ACTIVE.value:
        tx = sdk.sessions.EndSession(session_id=session.id, rating=0)
        print(sdk.sessions.wait_for_tx(tx["hash"]))

tx = sdk.sessions.StartSession(subscription_id=int(subscription_id), address=node_address)
tx_response = sdk.sessions.wait_for_tx(tx["hash"])

session_id = search_attribute(
    tx_response, "sentinel.session.v2.EventStart", "id"
)
# Double verify the session
session = sdk.sessions.QuerySession(int(session_id))
assert (
    session.id == int(session_id)
    and session.node_address == node_address
    and session.subscription_id == int(subscription_id)
)

print(sdk.nodes.PostSession(int(session_id), node.remote_url, NodeType(node_status["result"]["type"])))
