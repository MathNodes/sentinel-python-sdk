import grpc
import ssl
import time
from typing import Any
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from sentinel_sdk.types import NodeType, TxParams
from mospy import Transaction

class Transactor:
    def __init__(
        self,
        account,
        client
    ):
        self._account = account
        self._client = client

    # TODO: subscribe_to_gigabytes, subscribe_to_hours, start_request and all method should have fee denom and amount as args?
    # We need to find a good way to this. **The method could return only the MsgRequest and type_url**
    # Who wants to submit the tx, can call transaction (we should also implement multi-add_raw_msg), one tx with multiple msg

    def PrepareOrTransactMsg(   self, 
                                msg: Any, 
                                transact: bool = False,
                                tx_params : TxParams = TxParams(),
                                **kwargs):
        msg_args = {
            k: kwargs[k] for k in kwargs if k in ["address", "node_address", "id", "gigabytes", "hours", "rating", "denom"]
        }
                                    
        msg_args['frm'] = self.__account.address
        prepared_msg = msg(**msg_args)

        return self.transaction([prepared_msg], tx_params) if transact else prepared_msg


    def transaction(
        self,
        messages: list,
        tx_params: TxParams = TxParams(),
    ) -> dict:
        tx = Transaction(
            account=self._account,
            fee=Coin(denom=tx_params.denom, amount=f"{tx_params.fee_amount}"),
            gas=tx_params.gas,
            protobuf="sentinel",
            chain_id="sentinelhub-2",
        )

        if not isinstance(messages, list):
            messages = [messages]

        for message in messages:
            tx.add_raw_msg(message, type_url=f"/{message.DESCRIPTOR.full_name}")

        # Required before each tx of we get account sequence mismatch, expected 945, got 944: incorrect account sequence
        self._client.load_account_data(account=self._account)

        # inplace, auto-update gas with update=True
        # auto calculate the gas only if was not already passed as args:
        if tx_params.gas == 0:
            self._client.estimate_gas(
                transaction=tx, update=True, multiplier=tx_params.gas_multiplier
            )

        tx_response = self._client.broadcast_transaction(transaction=tx)
        # tx_response = {"hash": hash, "code": code, "log": log}
        return tx_response

    def wait_transaction(
        self, tx_hash: str, timeout: float = 120, pool_period: float = 10
    ):
        start = time.time()
        while 1:
            try:
                return self._client.get_tx(tx_hash)
            except grpc.RpcError as rpc_error:
                # https://github.com/grpc/grpc/tree/master/examples/python/errors
                # Instance of 'RpcError' has no 'code' member, work on runtime
                status_code = rpc_error.code()  # pylint: disable=no-member
                if status_code == grpc.StatusCode.NOT_FOUND:
                    if time.time() - start > timeout:
                        return None
                    time.sleep(pool_period)
