import copy
from typing import Any

import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2

"""
# https://github.com/cosmos/cosmos-sdk/blob/main/types/query/pagination.pb.go

// key is a value returned in PageResponse.next_key to begin
// querying the next page most efficiently. Only one of offset or key should be set.
Key []byte `protobuf:"bytes,1,opt,name=key,proto3" json:"key,omitempty"`

// offset is a numeric offset that can be used when key is unavailable.
// It is less efficient than using key. Only one of offset or key should be set.
Offset uint64 `protobuf:"varint,2,opt,name=offset,proto3" json:"offset,omitempty"`

// limit is the total number of results to be returned in the result page.
// If left empty it will default to a value to be set by each app.
Limit uint64 `protobuf:"varint,3,opt,name=limit,proto3" json:"limit,omitempty"`

// count_total is set to true  to indicate that the result set should include
// a count of the total number of items available for pagination in UIs.
// count_total is only respected when offset is used. It is ignored when key is set.
CountTotal bool `protobuf:"varint,4,opt,name=count_total,json=countTotal,proto3" json:"count_total,omitempty"`

// reverse is set to true if results are to be returned in the descending order.
// Since: cosmos-sdk 0.43
Reverse bool `protobuf:"varint,5,opt,name=reverse,proto3" json:"reverse,omitempty"`
"""

# TODO: implement offset iteration
# https://github.com/sentinel-official/hub/blob/development/x/node/types/querier_test.go#L40-L45


class Querier:
    def QueryAll(
        self,
        query: Any,
        request: Any,
        attribute: str,
        args: dict = {},
        limit: int = 500,
    ) -> list:
        request_arguments = copy.copy(args)

        items = []
        next_key = 0x01

        while next_key:
            pagination = {"limit": 500}
            if next_key != 0x01:
                pagination["key"] = next_key

            request_arguments["pagination"] = cosmos_pagination_pb2.PageRequest(
                **pagination
            )

            r = query(request(**request_arguments))
            next_key = r.pagination.next_key
            items += [item for item in getattr(r, attribute)]

        return items
