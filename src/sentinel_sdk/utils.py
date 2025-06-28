import json
import base64

# TODO: we want to move this method (?)
# In the latest version of mospy the response was converted as dict
# from google.protobuf.json_format import MessageToDict
# https://github.com/ctrl-Felix/mospy/blob/ea07705b6ec4c76cc355b7dc933fae7c09fd8429/src/mospy/clients/GRPCClient.py#L155
def search_attribute(tx_response: dict, event_type: str, attribute_key: str) -> dict:
    for event in tx_response.get("txResponse", tx_response).get("events", []):
        if event["type"] == event_type:
            for attribute in event["attributes"]:
                if base64.b64decode(attribute["key"]) == attribute_key.encode():
                    return json.loads(base64.b64decode(attribute["value"]).decode("utf-8"))
    return None
