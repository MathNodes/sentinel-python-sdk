# https://github.com/MathNodes/cosmospy-protobuf/blob/chain/sentinel/src/sentinel_protobuf/sentinel/types/v1/status.proto
from enum import Enum
# https://github.com/cosmos/cosmos-sdk/blob/main/types/query/pagination.pb.go
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2

from dataclasses import dataclass

class Status(Enum):
    UNSPECIFIED = 0
    ACTIVE = 1
    INACTIVE_PENDING = 2
    INACTIVE = 3

    def __str__(self):
        return f"Status{self.name.title()}"


class NodeType(Enum):
    WIREGUARD = 1
    V2RAY = 2

@dataclass
class TxParams:
    denom: str = "udvpn"
    fee_amount: int = 20000
    gas: float = 0
    gas_multiplier: float = 1.5


class PageRequest:
    """
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

    # https://github.com/sentinel-official/hub/blob/development/x/node/types/querier_test.go#L40-L45
    """

    def __init__(
        self,
        limit: int = 100,
        offset: int = None,
        count_total: bool = True,
        reverse: bool = False,
    ):
        self.limit = limit
        self.offset = offset
        self.count_total = count_total
        self.reverse = reverse

    def build(self, key: bytes = None):
        args = {"limit": self.limit}
        # If key is set --> [It is less efficient than using key. Only one of offset or key should be set]
        if key not in [0x01, None]:
            args["key"] = key
        elif self.offset is not None:
            args["offset"] = self.offset
            args["count_total"] = self.count_total
            args["reverse"] = self.reverse
        return cosmos_pagination_pb2.PageRequest(**args)

    def __str__(self):
        return f"PageRequest(limit={self.limit}, offset={self.offset}, count_total={self.count_total}, reverse={self.reverse})"

    def __repr__(self):
        return f"PageRequest(limit={self.limit}, offset={self.offset}, count_total={self.count_total}, reverse={self.reverse})"
