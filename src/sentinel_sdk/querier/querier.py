import copy
from typing import Any

import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2


class Querier:
    def QueryAll(
        self, query: Any, request: Any, attribute: str, args: dict = {}
    ) -> list:
        request_arguments = copy.copy(args)

        items = []
        next_key = 0x01

        while next_key:
            if next_key != 0x01:
                request_arguments["pagination"] = cosmos_pagination_pb2.PageRequest(
                    key=next_key
                )

            r = query(request(**request_arguments))
            next_key = r.pagination.next_key
            items += [item for item in getattr(r, attribute)]

        return items
