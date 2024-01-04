import json
from typing import Any

# TODO: we want to move this method (?)
def search_attribute(tx_response: Any, event_type: str, attribute_key: str) -> Any:
    for event in (tx_response.tx_response or tx_response).events:
        if event.type == event_type:
            for attribute in event.attributes:
                if attribute.key == attribute_key.encode():
                    return json.loads(attribute.value)
    return None
