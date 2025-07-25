from __future__ import absolute_import

import collections

from kafka.protocol.api import Request, Response
from kafka.protocol.struct import Struct
from kafka.protocol.types import Array, Bytes, Int16, Int32, Schema, String


DEFAULT_GENERATION_ID = -1
UNKNOWN_MEMBER_ID = ''

GroupMember = collections.namedtuple("GroupMember", ["member_id", "group_instance_id", "metadata_bytes"])
GroupMember.__new__.__defaults__ = (None,) * len(GroupMember._fields)


class JoinGroupResponse_v0(Response):
    API_KEY = 11
    API_VERSION = 0
    SCHEMA = Schema(
        ('error_code', Int16),
        ('generation_id', Int32),
        ('group_protocol', String('utf-8')),
        ('leader_id', String('utf-8')),
        ('member_id', String('utf-8')),
        ('members', Array(
            ('member_id', String('utf-8')),
            ('member_metadata', Bytes)))
    )


class JoinGroupResponse_v1(Response):
    API_KEY = 11
    API_VERSION = 1
    SCHEMA = JoinGroupResponse_v0.SCHEMA


class JoinGroupResponse_v2(Response):
    API_KEY = 11
    API_VERSION = 2
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('generation_id', Int32),
        ('group_protocol', String('utf-8')),
        ('leader_id', String('utf-8')),
        ('member_id', String('utf-8')),
        ('members', Array(
            ('member_id', String('utf-8')),
            ('member_metadata', Bytes)))
    )


class JoinGroupResponse_v3(Response):
    API_KEY = 11
    API_VERSION = 3
    SCHEMA = JoinGroupResponse_v2.SCHEMA


class JoinGroupResponse_v4(Response):
    API_KEY = 11
    API_VERSION = 4
    SCHEMA = JoinGroupResponse_v3.SCHEMA


class JoinGroupResponse_v5(Response):
    API_KEY = 11
    API_VERSION = 5
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('generation_id', Int32),
        ('group_protocol', String('utf-8')),
        ('leader_id', String('utf-8')),
        ('member_id', String('utf-8')),
        ('members', Array(
            ('member_id', String('utf-8')),
            ('group_instance_id', String('utf-8')),
            ('member_metadata', Bytes)))
    )


class JoinGroupRequest_v0(Request):
    API_KEY = 11
    API_VERSION = 0
    RESPONSE_TYPE = JoinGroupResponse_v0
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('session_timeout', Int32),
        ('member_id', String('utf-8')),
        ('protocol_type', String('utf-8')),
        ('group_protocols', Array(
            ('protocol_name', String('utf-8')),
            ('protocol_metadata', Bytes)))
    )


class JoinGroupRequest_v1(Request):
    API_KEY = 11
    API_VERSION = 1
    RESPONSE_TYPE = JoinGroupResponse_v1
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('session_timeout', Int32),
        ('rebalance_timeout', Int32),
        ('member_id', String('utf-8')),
        ('protocol_type', String('utf-8')),
        ('group_protocols', Array(
            ('protocol_name', String('utf-8')),
            ('protocol_metadata', Bytes)))
    )


class JoinGroupRequest_v2(Request):
    API_KEY = 11
    API_VERSION = 2
    RESPONSE_TYPE = JoinGroupResponse_v2
    SCHEMA = JoinGroupRequest_v1.SCHEMA


class JoinGroupRequest_v3(Request):
    API_KEY = 11
    API_VERSION = 3
    RESPONSE_TYPE = JoinGroupResponse_v3
    SCHEMA = JoinGroupRequest_v2.SCHEMA


class JoinGroupRequest_v4(Request):
    API_KEY = 11
    API_VERSION = 4
    RESPONSE_TYPE = JoinGroupResponse_v4
    SCHEMA = JoinGroupRequest_v3.SCHEMA


class JoinGroupRequest_v5(Request):
    API_KEY = 11
    API_VERSION = 5
    RESPONSE_TYPE = JoinGroupResponse_v5
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('session_timeout', Int32),
        ('rebalance_timeout', Int32),
        ('member_id', String('utf-8')),
        ('group_instance_id', String('utf-8')),
        ('protocol_type', String('utf-8')),
        ('group_protocols', Array(
            ('protocol_name', String('utf-8')),
            ('protocol_metadata', Bytes)))
    )


JoinGroupRequest = [
    JoinGroupRequest_v0, JoinGroupRequest_v1, JoinGroupRequest_v2,
    JoinGroupRequest_v3, JoinGroupRequest_v4, JoinGroupRequest_v5,

]
JoinGroupResponse = [
    JoinGroupResponse_v0, JoinGroupResponse_v1, JoinGroupResponse_v2,
    JoinGroupResponse_v3, JoinGroupResponse_v4, JoinGroupResponse_v5,
]


class ProtocolMetadata(Struct):
    SCHEMA = Schema(
        ('version', Int16),
        ('subscription', Array(String('utf-8'))), # topics list
        ('user_data', Bytes)
    )


class SyncGroupResponse_v0(Response):
    API_KEY = 14
    API_VERSION = 0
    SCHEMA = Schema(
        ('error_code', Int16),
        ('member_assignment', Bytes)
    )


class SyncGroupResponse_v1(Response):
    API_KEY = 14
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('member_assignment', Bytes)
    )


class SyncGroupResponse_v2(Response):
    API_KEY = 14
    API_VERSION = 2
    SCHEMA = SyncGroupResponse_v1.SCHEMA


class SyncGroupResponse_v3(Response):
    API_KEY = 14
    API_VERSION = 3
    SCHEMA = SyncGroupResponse_v2.SCHEMA


class SyncGroupRequest_v0(Request):
    API_KEY = 14
    API_VERSION = 0
    RESPONSE_TYPE = SyncGroupResponse_v0
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('generation_id', Int32),
        ('member_id', String('utf-8')),
        ('group_assignment', Array(
            ('member_id', String('utf-8')),
            ('member_metadata', Bytes)))
    )


class SyncGroupRequest_v1(Request):
    API_KEY = 14
    API_VERSION = 1
    RESPONSE_TYPE = SyncGroupResponse_v1
    SCHEMA = SyncGroupRequest_v0.SCHEMA


class SyncGroupRequest_v2(Request):
    API_KEY = 14
    API_VERSION = 2
    RESPONSE_TYPE = SyncGroupResponse_v2
    SCHEMA = SyncGroupRequest_v1.SCHEMA


class SyncGroupRequest_v3(Request):
    API_KEY = 14
    API_VERSION = 3
    RESPONSE_TYPE = SyncGroupResponse_v3
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('generation_id', Int32),
        ('member_id', String('utf-8')),
        ('group_instance_id', String('utf-8')),
        ('group_assignment', Array(
            ('member_id', String('utf-8')),
            ('member_metadata', Bytes)))
    )


SyncGroupRequest = [
    SyncGroupRequest_v0, SyncGroupRequest_v1, SyncGroupRequest_v2,
    SyncGroupRequest_v3,
]
SyncGroupResponse = [
    SyncGroupResponse_v0, SyncGroupResponse_v1, SyncGroupResponse_v2,
    SyncGroupResponse_v3,
]


class MemberAssignment(Struct):
    SCHEMA = Schema(
        ('version', Int16),
        ('assignment', Array(
            ('topic', String('utf-8')),
            ('partitions', Array(Int32)))),
        ('user_data', Bytes)
    )


class HeartbeatResponse_v0(Response):
    API_KEY = 12
    API_VERSION = 0
    SCHEMA = Schema(
        ('error_code', Int16)
    )


class HeartbeatResponse_v1(Response):
    API_KEY = 12
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16)
    )


class HeartbeatResponse_v2(Response):
    API_KEY = 12
    API_VERSION = 2
    SCHEMA = HeartbeatResponse_v1.SCHEMA


class HeartbeatResponse_v3(Response):
    API_KEY = 12
    API_VERSION = 3
    SCHEMA = HeartbeatResponse_v2.SCHEMA


class HeartbeatRequest_v0(Request):
    API_KEY = 12
    API_VERSION = 0
    RESPONSE_TYPE = HeartbeatResponse_v0
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('generation_id', Int32),
        ('member_id', String('utf-8'))
    )


class HeartbeatRequest_v1(Request):
    API_KEY = 12
    API_VERSION = 1
    RESPONSE_TYPE = HeartbeatResponse_v1
    SCHEMA = HeartbeatRequest_v0.SCHEMA


class HeartbeatRequest_v2(Request):
    API_KEY = 12
    API_VERSION = 2
    RESPONSE_TYPE = HeartbeatResponse_v2
    SCHEMA = HeartbeatRequest_v1.SCHEMA


class HeartbeatRequest_v3(Request):
    API_KEY = 12
    API_VERSION = 3
    RESPONSE_TYPE = HeartbeatResponse_v3
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('generation_id', Int32),
        ('member_id', String('utf-8')),
        ('group_instance_id', String('utf-8'))
    )


HeartbeatRequest = [
    HeartbeatRequest_v0, HeartbeatRequest_v1, HeartbeatRequest_v2,
    HeartbeatRequest_v3,
]
HeartbeatResponse = [
    HeartbeatResponse_v0, HeartbeatResponse_v1, HeartbeatResponse_v2,
    HeartbeatResponse_v3,
]


class LeaveGroupResponse_v0(Response):
    API_KEY = 13
    API_VERSION = 0
    SCHEMA = Schema(
        ('error_code', Int16)
    )


class LeaveGroupResponse_v1(Response):
    API_KEY = 13
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16)
    )


class LeaveGroupResponse_v2(Response):
    API_KEY = 13
    API_VERSION = 2
    SCHEMA = LeaveGroupResponse_v1.SCHEMA


class LeaveGroupResponse_v3(Response):
    API_KEY = 13
    API_VERSION = 3
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('members', Array(
            ('member_id', String('utf-8')),
            ('group_instance_id', String('utf-8')),
            ('error_code', Int16)))
    )


class LeaveGroupRequest_v0(Request):
    API_KEY = 13
    API_VERSION = 0
    RESPONSE_TYPE = LeaveGroupResponse_v0
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('member_id', String('utf-8'))
    )


class LeaveGroupRequest_v1(Request):
    API_KEY = 13
    API_VERSION = 1
    RESPONSE_TYPE = LeaveGroupResponse_v1
    SCHEMA = LeaveGroupRequest_v0.SCHEMA


class LeaveGroupRequest_v2(Request):
    API_KEY = 13
    API_VERSION = 2
    RESPONSE_TYPE = LeaveGroupResponse_v2
    SCHEMA = LeaveGroupRequest_v1.SCHEMA


class LeaveGroupRequest_v3(Request):
    API_KEY = 13
    API_VERSION = 3
    RESPONSE_TYPE = LeaveGroupResponse_v3
    SCHEMA = Schema(
        ('group', String('utf-8')),
        ('members', Array(
            ('member_id', String('utf-8')),
            ('group_instance_id', String('utf-8'))))
    )


LeaveGroupRequest = [
    LeaveGroupRequest_v0, LeaveGroupRequest_v1, LeaveGroupRequest_v2,
    LeaveGroupRequest_v3,
]
LeaveGroupResponse = [
    LeaveGroupResponse_v0, LeaveGroupResponse_v1, LeaveGroupResponse_v2,
    LeaveGroupResponse_v3,
]
