from typing import Any

from sentinel_sdk.types import PageRequest


class Querier:
    def QueryAll(
        self,
        query: Any,
        request: Any,
        attribute: str,
        pagination: PageRequest = None,
        **kwargs,
    ) -> list:
        # ["status", "address", "id"] are the only valid kwargs
        request_arguments = {
            k: kwargs[k] for k in kwargs if k in ["status", "address", "id"]
        }

        if pagination is None:
            # Create an empty page request, will be used for pagination with next_key
            # On first iteration with next_key = 0x01, the pagination will have only limit value
            pagination = PageRequest()

        items = []
        next_key = 0x01

        while next_key:
            request_arguments["pagination"] = pagination.build(key=next_key)
            r = query(request(**request_arguments))
            next_key = r.pagination.next_key
            items += [item for item in getattr(r, attribute)]

            # Stop iteration if PageRequest contain a offset value
            if pagination.offset is not None:
                break

        return items