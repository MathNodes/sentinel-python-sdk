import json
import base64
from collections import OrderedDict

# TODO: we want to move this method (?)
# In the latest version of mospy the response was converted as dict
# from google.protobuf.json_format import MessageToDict
# https://github.com/ctrl-Felix/mospy/blob/ea07705b6ec4c76cc355b7dc933fae7c09fd8429/src/mospy/clients/GRPCClient.py#L155
def search_attribute(tx_response: dict, event_type: str, attribute_key: str) -> dict:
    tx_response = ordered_dict_to_dict(tx_response)
    for event in tx_response.get("txResponse", tx_response).get("events", []):
        if event["type"] == event_type:
            for attribute in event["attributes"]:
                if attribute["key"] == attribute_key:
                    return json.loads(attribute["value"])
    return None
    

def ordered_dict_to_dict(od):
    return {k: (ordered_dict_to_dict(v) if isinstance(v, OrderedDict) else v) for k, v in od.items()}
