import json

import grpc
from sentinel_protobuf.sentinel.node.v2.msg_pb2 import MsgSubscribeRequest
from sentinel_protobuf.sentinel.session.v2.msg_pb2 import MsgEndRequest, MsgStartRequest

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import NodeType, TxParams

# GRPC_VERBOSITY=debug GRPC_TRACE=tcp,http python test/queryall.py

# NEVER SHARE YOUR SECRET!
secret = "abdc efgh 1234 5678"

sdk = SDKInstance(grpcaddr="grpc.sentinel.co", grpcport=9090, secret=secret)
node_address = "sentnode1234abcd"
node = sdk.multiquerier.node_querier.QueryNode(node_address)
node_status = json.loads(sdk.multiquerier.node_querier.QueryNodeStatus(node))

try:
    # tx = sdk.transactor.subscribe_to_gigabytes(node_address=node_address, gigabytes=1)
    tx = sdk.transactor.PrepareOrTransactMsg(
        MsgSubscribeRequest,
        node_address=node_address,
        gigabytes=1,
        hours=0,
        denom="udvpn",  # Comment this, raise exception
        transact=True,
    )
except grpc.RpcError as rpc_error:
    # TODO: this should be handled on skd side
    print(rpc_error.code())  # pylint: disable=no-member
    print(rpc_error.details())  # pylint: disable=no-member
    print(rpc_error.debug_error_string())  # pylint: disable=no-member

tx_response = sdk.transactor.wait_transaction(tx["hash"])
subscription_id = sdk.transactor.search_attribute(
    tx_response, "sentinel.node.v2.EventCreateSubscription", "id"
)

# Double verify the subscription
subscription = sdk.multiquerier.subscription_querier.QuerySubscription(
    int(subscription_id)
)
assert (
    subscription.base.id == int(subscription_id)
    and subscription.node_address == node_address
)

sessions = sdk.multiquerier.session_querier.QuerySessionsForSubscription(
    subscription.base.id
)
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
    tx_response = sdk.transactor.wait_transaction(tx["hash"])
except grpc.RpcError as rpc_error:
    # TODO: this should be handled on skd side
    print(rpc_error.code())  # pylint: disable=no-member
    print(rpc_error.details())  # pylint: disable=no-member
    print(rpc_error.debug_error_string())  # pylint: disable=no-member

session_id = sdk.transactor.search_attribute(
    tx_response, "sentinel.session.v2.EventStart", "id"
)
# Double verify the session
session = sdk.multiquerier.session_querier.QuerySession(int(session_id))
assert (
    session.id == int(session_id)
    and session.node_address == node_address
    and session.subscription_id == int(subscription_id)
)

print(
    sdk.transactor.post_session(
        int(session_id), node.remote_url, NodeType(node_status["result"]["type"])
    )
)
