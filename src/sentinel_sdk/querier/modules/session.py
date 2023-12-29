import grpc
import sentinel_protobuf.cosmos.base.query.v1beta1.pagination_pb2 as cosmos_pagination_pb2
import sentinel_protobuf.sentinel.session.v2.querier_pb2 as sentinel_session_v2_querier_pb2
import sentinel_protobuf.sentinel.session.v2.querier_pb2_grpc as sentinel_session_v2_querier_pb2_grpc


class SessionQuerier:
    def __init__(self, channel):
        self.__channel = channel
        self.__stub = sentinel_session_v2_querier_pb2_grpc.QueryServiceStub(
            self.__channel
        )

    def QuerySession(self, sess_id: int):
        try:
            r = self.__stub.QuerySession(
                sentinel_session_v2_querier_pb2.QuerySessionRequest(id=sess_id)
            )
        except grpc._channel._InactiveRpcError as e:
            print(e)
            return None

        return r.session

    def QuerySessions(self):
        fetched_sessions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySessions(
                    sentinel_session_v2_querier_pb2.QuerySessionsRequest()
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySessions(
                    sentinel_session_v2_querier_pb2.QuerySessionsRequest(
                        pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.sessions:
                fetched_sessions.append(s)

        return fetched_sessions

    def QuerySessionsForAccount(self, address: str):
        fetched_sessions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySessionsForAccount(
                    sentinel_session_v2_querier_pb2.QuerySessionsForAccountRequest(
                        address=address
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySessionsForAccount(
                    sentinel_session_v2_querier_pb2.QuerySessionsForAccountRequest(
                        address=address, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.sessions:
                fetched_sessions.append(s)

        return fetched_sessions

    def QuerySessionsForAllocation(self, address: str, alloc_id: int):
        fetched_sessions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySessionsForAllocation(
                    sentinel_session_v2_querier_pb2.QuerySessionsForAllocationRequest(
                        address=address, id=alloc_id
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySessionsForAllocation(
                    sentinel_session_v2_querier_pb2.QuerySessionsForAllocationRequest(
                        address=address, id=alloc_id, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.sessions:
                fetched_sessions.append(s)

        return fetched_sessions

    def QuerySessionsForNode(self, address: str):
        fetched_sessions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySessionsForNode(
                    sentinel_session_v2_querier_pb2.QuerySessionsForNodeRequest(
                        address=address
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySessionsForNode(
                    sentinel_session_v2_querier_pb2.QuerySessionsForNodeRequest(
                        address=address, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.sessions:
                fetched_sessions.append(s)

        return fetched_sessions

    def QuerySessionsForSubscription(self, subscr_id: int):
        fetched_sessions = []
        next_key = 0x01

        while next_key:
            if next_key == 0x01:
                r = self.__stub.QuerySessionsForSubscription(
                    sentinel_session_v2_querier_pb2.QuerySessionsForSubscriptionRequest(
                        id=subscr_id
                    )
                )
            else:
                next_page_req = cosmos_pagination_pb2.PageRequest(key=next_key)
                r = self.__stub.QuerySessionsForSubscription(
                    sentinel_session_v2_querier_pb2.QuerySessionsForSubscriptionRequest(
                        id=subscr_id, pagination=next_page_req
                    )
                )

            next_key = r.pagination.next_key
            for s in r.sessions:
                fetched_sessions.append(s)

        return fetched_sessions
