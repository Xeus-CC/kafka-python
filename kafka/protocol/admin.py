from __future__ import absolute_import

# enum in stdlib as of py3.4
try:
    from enum import IntEnum  # pylint: disable=import-error
except ImportError:
    # vendored backport module
    from kafka.vendor.enum34 import IntEnum

from kafka.protocol.api import Request, Response
from kafka.protocol.types import Array, Boolean, Bytes, Int8, Int16, Int32, Int64, Schema, String, Float64, CompactString, CompactArray, TaggedFields, BitField


class CreateTopicsResponse_v0(Response):
    API_KEY = 19
    API_VERSION = 0
    SCHEMA = Schema(
        ('topic_errors', Array(
            ('topic', String('utf-8')),
            ('error_code', Int16)))
    )


class CreateTopicsResponse_v1(Response):
    API_KEY = 19
    API_VERSION = 1
    SCHEMA = Schema(
        ('topic_errors', Array(
            ('topic', String('utf-8')),
            ('error_code', Int16),
            ('error_message', String('utf-8'))))
    )


class CreateTopicsResponse_v2(Response):
    API_KEY = 19
    API_VERSION = 2
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('topic_errors', Array(
            ('topic', String('utf-8')),
            ('error_code', Int16),
            ('error_message', String('utf-8'))))
    )

class CreateTopicsResponse_v3(Response):
    API_KEY = 19
    API_VERSION = 3
    SCHEMA = CreateTopicsResponse_v2.SCHEMA


class CreateTopicsRequest_v0(Request):
    API_KEY = 19
    API_VERSION = 0
    RESPONSE_TYPE = CreateTopicsResponse_v0
    SCHEMA = Schema(
        ('create_topic_requests', Array(
            ('topic', String('utf-8')),
            ('num_partitions', Int32),
            ('replication_factor', Int16),
            ('replica_assignment', Array(
                ('partition_id', Int32),
                ('replicas', Array(Int32)))),
            ('configs', Array(
                ('config_key', String('utf-8')),
                ('config_value', String('utf-8')))))),
        ('timeout', Int32)
    )


class CreateTopicsRequest_v1(Request):
    API_KEY = 19
    API_VERSION = 1
    RESPONSE_TYPE = CreateTopicsResponse_v1
    SCHEMA = Schema(
        ('create_topic_requests', Array(
            ('topic', String('utf-8')),
            ('num_partitions', Int32),
            ('replication_factor', Int16),
            ('replica_assignment', Array(
                ('partition_id', Int32),
                ('replicas', Array(Int32)))),
            ('configs', Array(
                ('config_key', String('utf-8')),
                ('config_value', String('utf-8')))))),
        ('timeout', Int32),
        ('validate_only', Boolean)
    )


class CreateTopicsRequest_v2(Request):
    API_KEY = 19
    API_VERSION = 2
    RESPONSE_TYPE = CreateTopicsResponse_v2
    SCHEMA = CreateTopicsRequest_v1.SCHEMA


class CreateTopicsRequest_v3(Request):
    API_KEY = 19
    API_VERSION = 3
    RESPONSE_TYPE = CreateTopicsResponse_v3
    SCHEMA = CreateTopicsRequest_v1.SCHEMA


CreateTopicsRequest = [
    CreateTopicsRequest_v0, CreateTopicsRequest_v1,
    CreateTopicsRequest_v2, CreateTopicsRequest_v3,
]
CreateTopicsResponse = [
    CreateTopicsResponse_v0, CreateTopicsResponse_v1,
    CreateTopicsResponse_v2, CreateTopicsResponse_v3,
]


class DeleteTopicsResponse_v0(Response):
    API_KEY = 20
    API_VERSION = 0
    SCHEMA = Schema(
        ('topic_error_codes', Array(
            ('topic', String('utf-8')),
            ('error_code', Int16)))
    )


class DeleteTopicsResponse_v1(Response):
    API_KEY = 20
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('topic_error_codes', Array(
            ('topic', String('utf-8')),
            ('error_code', Int16)))
    )


class DeleteTopicsResponse_v2(Response):
    API_KEY = 20
    API_VERSION = 2
    SCHEMA = DeleteTopicsResponse_v1.SCHEMA


class DeleteTopicsResponse_v3(Response):
    API_KEY = 20
    API_VERSION = 3
    SCHEMA = DeleteTopicsResponse_v1.SCHEMA


class DeleteTopicsRequest_v0(Request):
    API_KEY = 20
    API_VERSION = 0
    RESPONSE_TYPE = DeleteTopicsResponse_v0
    SCHEMA = Schema(
        ('topics', Array(String('utf-8'))),
        ('timeout', Int32)
    )


class DeleteTopicsRequest_v1(Request):
    API_KEY = 20
    API_VERSION = 1
    RESPONSE_TYPE = DeleteTopicsResponse_v1
    SCHEMA = DeleteTopicsRequest_v0.SCHEMA


class DeleteTopicsRequest_v2(Request):
    API_KEY = 20
    API_VERSION = 2
    RESPONSE_TYPE = DeleteTopicsResponse_v2
    SCHEMA = DeleteTopicsRequest_v0.SCHEMA


class DeleteTopicsRequest_v3(Request):
    API_KEY = 20
    API_VERSION = 3
    RESPONSE_TYPE = DeleteTopicsResponse_v3
    SCHEMA = DeleteTopicsRequest_v0.SCHEMA


DeleteTopicsRequest = [
    DeleteTopicsRequest_v0, DeleteTopicsRequest_v1,
    DeleteTopicsRequest_v2, DeleteTopicsRequest_v3,
]
DeleteTopicsResponse = [
    DeleteTopicsResponse_v0, DeleteTopicsResponse_v1,
    DeleteTopicsResponse_v2, DeleteTopicsResponse_v3,
]


class DeleteRecordsResponse_v0(Response):
    API_KEY = 21
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('topics', Array(
            ('name', String('utf-8')),
            ('partitions', Array(
                ('partition_index', Int32),
                ('low_watermark', Int64),
                ('error_code', Int16))))),
    )


class DeleteRecordsRequest_v0(Request):
    API_KEY = 21
    API_VERSION = 0
    RESPONSE_TYPE = DeleteRecordsResponse_v0
    SCHEMA = Schema(
        ('topics', Array(
            ('name', String('utf-8')),
            ('partitions', Array(
                ('partition_index', Int32),
                ('offset', Int64))))),
        ('timeout_ms', Int32)
    )


DeleteRecordsResponse = [DeleteRecordsResponse_v0]
DeleteRecordsRequest = [DeleteRecordsRequest_v0]


class ListGroupsResponse_v0(Response):
    API_KEY = 16
    API_VERSION = 0
    SCHEMA = Schema(
        ('error_code', Int16),
        ('groups', Array(
            ('group', String('utf-8')),
            ('protocol_type', String('utf-8'))))
    )


class ListGroupsResponse_v1(Response):
    API_KEY = 16
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('groups', Array(
            ('group', String('utf-8')),
            ('protocol_type', String('utf-8'))))
    )

class ListGroupsResponse_v2(Response):
    API_KEY = 16
    API_VERSION = 2
    SCHEMA = ListGroupsResponse_v1.SCHEMA


class ListGroupsRequest_v0(Request):
    API_KEY = 16
    API_VERSION = 0
    RESPONSE_TYPE = ListGroupsResponse_v0
    SCHEMA = Schema()


class ListGroupsRequest_v1(Request):
    API_KEY = 16
    API_VERSION = 1
    RESPONSE_TYPE = ListGroupsResponse_v1
    SCHEMA = ListGroupsRequest_v0.SCHEMA

class ListGroupsRequest_v2(Request):
    API_KEY = 16
    API_VERSION = 1
    RESPONSE_TYPE = ListGroupsResponse_v2
    SCHEMA = ListGroupsRequest_v0.SCHEMA


ListGroupsRequest = [
    ListGroupsRequest_v0, ListGroupsRequest_v1,
    ListGroupsRequest_v2,
]
ListGroupsResponse = [
    ListGroupsResponse_v0, ListGroupsResponse_v1,
    ListGroupsResponse_v2,
]


class DescribeGroupsResponse_v0(Response):
    API_KEY = 15
    API_VERSION = 0
    SCHEMA = Schema(
        ('groups', Array(
            ('error_code', Int16),
            ('group', String('utf-8')),
            ('state', String('utf-8')),
            ('protocol_type', String('utf-8')),
            ('protocol', String('utf-8')),
            ('members', Array(
                ('member_id', String('utf-8')),
                ('client_id', String('utf-8')),
                ('client_host', String('utf-8')),
                ('member_metadata', Bytes),
                ('member_assignment', Bytes)))))
    )


class DescribeGroupsResponse_v1(Response):
    API_KEY = 15
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('groups', Array(
            ('error_code', Int16),
            ('group', String('utf-8')),
            ('state', String('utf-8')),
            ('protocol_type', String('utf-8')),
            ('protocol', String('utf-8')),
            ('members', Array(
                ('member_id', String('utf-8')),
                ('client_id', String('utf-8')),
                ('client_host', String('utf-8')),
                ('member_metadata', Bytes),
                ('member_assignment', Bytes)))))
    )


class DescribeGroupsResponse_v2(Response):
    API_KEY = 15
    API_VERSION = 2
    SCHEMA = DescribeGroupsResponse_v1.SCHEMA


class DescribeGroupsResponse_v3(Response):
    API_KEY = 15
    API_VERSION = 3
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('groups', Array(
            ('error_code', Int16),
            ('group', String('utf-8')),
            ('state', String('utf-8')),
            ('protocol_type', String('utf-8')),
            ('protocol', String('utf-8')),
            ('members', Array(
                ('member_id', String('utf-8')),
                ('client_id', String('utf-8')),
                ('client_host', String('utf-8')),
                ('member_metadata', Bytes),
                ('member_assignment', Bytes))),
            ('authorized_operations', BitField)))
    )


class DescribeGroupsRequest_v0(Request):
    API_KEY = 15
    API_VERSION = 0
    RESPONSE_TYPE = DescribeGroupsResponse_v0
    SCHEMA = Schema(
        ('groups', Array(String('utf-8')))
    )


class DescribeGroupsRequest_v1(Request):
    API_KEY = 15
    API_VERSION = 1
    RESPONSE_TYPE = DescribeGroupsResponse_v1
    SCHEMA = DescribeGroupsRequest_v0.SCHEMA


class DescribeGroupsRequest_v2(Request):
    API_KEY = 15
    API_VERSION = 2
    RESPONSE_TYPE = DescribeGroupsResponse_v2
    SCHEMA = DescribeGroupsRequest_v0.SCHEMA


class DescribeGroupsRequest_v3(Request):
    API_KEY = 15
    API_VERSION = 3
    RESPONSE_TYPE = DescribeGroupsResponse_v3
    SCHEMA = Schema(
        ('groups', Array(String('utf-8'))),
        ('include_authorized_operations', Boolean)
    )


DescribeGroupsRequest = [
    DescribeGroupsRequest_v0, DescribeGroupsRequest_v1,
    DescribeGroupsRequest_v2, DescribeGroupsRequest_v3,
]
DescribeGroupsResponse = [
    DescribeGroupsResponse_v0, DescribeGroupsResponse_v1,
    DescribeGroupsResponse_v2, DescribeGroupsResponse_v3,
]


class DescribeAclsResponse_v0(Response):
    API_KEY = 29
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('error_message', String('utf-8')),
        ('resources', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('acls', Array(
                ('principal', String('utf-8')),
                ('host', String('utf-8')),
                ('operation', Int8),
                ('permission_type', Int8)))))
    )


class DescribeAclsResponse_v1(Response):
    API_KEY = 29
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('error_message', String('utf-8')),
        ('resources', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('resource_pattern_type', Int8),
            ('acls', Array(
                ('principal', String('utf-8')),
                ('host', String('utf-8')),
                ('operation', Int8),
                ('permission_type', Int8)))))
    )


class DescribeAclsResponse_v2(Response):
    API_KEY = 29
    API_VERSION = 2
    SCHEMA = DescribeAclsResponse_v1.SCHEMA


class DescribeAclsRequest_v0(Request):
    API_KEY = 29
    API_VERSION = 0
    RESPONSE_TYPE = DescribeAclsResponse_v0
    SCHEMA = Schema(
        ('resource_type', Int8),
        ('resource_name', String('utf-8')),
        ('principal', String('utf-8')),
        ('host', String('utf-8')),
        ('operation', Int8),
        ('permission_type', Int8)
    )


class DescribeAclsRequest_v1(Request):
    API_KEY = 29
    API_VERSION = 1
    RESPONSE_TYPE = DescribeAclsResponse_v1
    SCHEMA = Schema(
        ('resource_type', Int8),
        ('resource_name', String('utf-8')),
        ('resource_pattern_type_filter', Int8),
        ('principal', String('utf-8')),
        ('host', String('utf-8')),
        ('operation', Int8),
        ('permission_type', Int8)
    )


class DescribeAclsRequest_v2(Request):
    """
    Enable flexible version
    """
    API_KEY = 29
    API_VERSION = 2
    RESPONSE_TYPE = DescribeAclsResponse_v2
    SCHEMA = DescribeAclsRequest_v1.SCHEMA


DescribeAclsRequest = [DescribeAclsRequest_v0, DescribeAclsRequest_v1, DescribeAclsRequest_v2]
DescribeAclsResponse = [DescribeAclsResponse_v0, DescribeAclsResponse_v1, DescribeAclsResponse_v2]

class CreateAclsResponse_v0(Response):
    API_KEY = 30
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('creation_responses', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8'))))
    )

class CreateAclsResponse_v1(Response):
    API_KEY = 30
    API_VERSION = 1
    SCHEMA = CreateAclsResponse_v0.SCHEMA

class CreateAclsRequest_v0(Request):
    API_KEY = 30
    API_VERSION = 0
    RESPONSE_TYPE = CreateAclsResponse_v0
    SCHEMA = Schema(
        ('creations', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('principal', String('utf-8')),
            ('host', String('utf-8')),
            ('operation', Int8),
            ('permission_type', Int8)))
    )

class CreateAclsRequest_v1(Request):
    API_KEY = 30
    API_VERSION = 1
    RESPONSE_TYPE = CreateAclsResponse_v1
    SCHEMA = Schema(
        ('creations', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('resource_pattern_type', Int8),
            ('principal', String('utf-8')),
            ('host', String('utf-8')),
            ('operation', Int8),
            ('permission_type', Int8)))
    )

CreateAclsRequest = [CreateAclsRequest_v0, CreateAclsRequest_v1]
CreateAclsResponse = [CreateAclsResponse_v0, CreateAclsResponse_v1]

class DeleteAclsResponse_v0(Response):
    API_KEY = 31
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('filter_responses', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8')),
            ('matching_acls', Array(
                ('error_code', Int16),
                ('error_message', String('utf-8')),
                ('resource_type', Int8),
                ('resource_name', String('utf-8')),
                ('principal', String('utf-8')),
                ('host', String('utf-8')),
                ('operation', Int8),
                ('permission_type', Int8)))))
    )

class DeleteAclsResponse_v1(Response):
    API_KEY = 31
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('filter_responses', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8')),
            ('matching_acls', Array(
                ('error_code', Int16),
                ('error_message', String('utf-8')),
                ('resource_type', Int8),
                ('resource_name', String('utf-8')),
                ('resource_pattern_type', Int8),
                ('principal', String('utf-8')),
                ('host', String('utf-8')),
                ('operation', Int8),
                ('permission_type', Int8)))))
    )

class DeleteAclsRequest_v0(Request):
    API_KEY = 31
    API_VERSION = 0
    RESPONSE_TYPE = DeleteAclsResponse_v0
    SCHEMA = Schema(
        ('filters', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('principal', String('utf-8')),
            ('host', String('utf-8')),
            ('operation', Int8),
            ('permission_type', Int8)))
    )

class DeleteAclsRequest_v1(Request):
    API_KEY = 31
    API_VERSION = 1
    RESPONSE_TYPE = DeleteAclsResponse_v1
    SCHEMA = Schema(
        ('filters', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('resource_pattern_type_filter', Int8),
            ('principal', String('utf-8')),
            ('host', String('utf-8')),
            ('operation', Int8),
            ('permission_type', Int8)))
    )

DeleteAclsRequest = [DeleteAclsRequest_v0, DeleteAclsRequest_v1]
DeleteAclsResponse = [DeleteAclsResponse_v0, DeleteAclsResponse_v1]

class AlterConfigsResponse_v0(Response):
    API_KEY = 33
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('resources', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8')),
            ('resource_type', Int8),
            ('resource_name', String('utf-8'))))
    )


class AlterConfigsResponse_v1(Response):
    API_KEY = 33
    API_VERSION = 1
    SCHEMA = AlterConfigsResponse_v0.SCHEMA


class AlterConfigsRequest_v0(Request):
    API_KEY = 33
    API_VERSION = 0
    RESPONSE_TYPE = AlterConfigsResponse_v0
    SCHEMA = Schema(
        ('resources', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('config_entries', Array(
                ('config_name', String('utf-8')),
                ('config_value', String('utf-8')))))),
        ('validate_only', Boolean)
    )

class AlterConfigsRequest_v1(Request):
    API_KEY = 33
    API_VERSION = 1
    RESPONSE_TYPE = AlterConfigsResponse_v1
    SCHEMA = AlterConfigsRequest_v0.SCHEMA

AlterConfigsRequest = [AlterConfigsRequest_v0, AlterConfigsRequest_v1]
AlterConfigsResponse = [AlterConfigsResponse_v0, AlterConfigsRequest_v1]


class DescribeConfigsResponse_v0(Response):
    API_KEY = 32
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('resources', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8')),
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('config_entries', Array(
                ('config_names', String('utf-8')),
                ('config_value', String('utf-8')),
                ('read_only', Boolean),
                ('is_default', Boolean),
                ('is_sensitive', Boolean)))))
    )

class DescribeConfigsResponse_v1(Response):
    API_KEY = 32
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('resources', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8')),
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('config_entries', Array(
                ('config_names', String('utf-8')),
                ('config_value', String('utf-8')),
                ('read_only', Boolean),
                ('config_source', Int8),
                ('is_sensitive', Boolean),
                ('config_synonyms', Array(
                    ('config_name', String('utf-8')),
                    ('config_value', String('utf-8')),
                    ('config_source', Int8)))))))
    )

class DescribeConfigsResponse_v2(Response):
    API_KEY = 32
    API_VERSION = 2
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('resources', Array(
            ('error_code', Int16),
            ('error_message', String('utf-8')),
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('config_entries', Array(
                ('config_names', String('utf-8')),
                ('config_value', String('utf-8')),
                ('read_only', Boolean),
                ('config_source', Int8),
                ('is_sensitive', Boolean),
                ('config_synonyms', Array(
                    ('config_name', String('utf-8')),
                    ('config_value', String('utf-8')),
                    ('config_source', Int8)))))))
    )

class DescribeConfigsRequest_v0(Request):
    API_KEY = 32
    API_VERSION = 0
    RESPONSE_TYPE = DescribeConfigsResponse_v0
    SCHEMA = Schema(
        ('resources', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('config_names', Array(String('utf-8')))))
    )

class DescribeConfigsRequest_v1(Request):
    API_KEY = 32
    API_VERSION = 1
    RESPONSE_TYPE = DescribeConfigsResponse_v1
    SCHEMA = Schema(
        ('resources', Array(
            ('resource_type', Int8),
            ('resource_name', String('utf-8')),
            ('config_names', Array(String('utf-8'))))),
        ('include_synonyms', Boolean)
    )


class DescribeConfigsRequest_v2(Request):
    API_KEY = 32
    API_VERSION = 2
    RESPONSE_TYPE = DescribeConfigsResponse_v2
    SCHEMA = DescribeConfigsRequest_v1.SCHEMA


DescribeConfigsRequest = [
    DescribeConfigsRequest_v0, DescribeConfigsRequest_v1,
    DescribeConfigsRequest_v2,
]
DescribeConfigsResponse = [
    DescribeConfigsResponse_v0, DescribeConfigsResponse_v1,
    DescribeConfigsResponse_v2,
]


class DescribeLogDirsResponse_v0(Response):
    API_KEY = 35
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('log_dirs', Array(
            ('error_code', Int16),
            ('log_dir', String('utf-8')),
            ('topics', Array(
                ('name', String('utf-8')),
                ('partitions', Array(
                    ('partition_index', Int32),
                    ('partition_size', Int64),
                    ('offset_lag', Int64),
                    ('is_future_key', Boolean)
                ))
            ))
        ))
    )


class DescribeLogDirsRequest_v0(Request):
    API_KEY = 35
    API_VERSION = 0
    RESPONSE_TYPE = DescribeLogDirsResponse_v0
    SCHEMA = Schema(
                     ('topics', Array(
                         ('topic', String('utf-8')),
                         ('partitions', Int32)
                         ))
                 )


DescribeLogDirsResponse = [
    DescribeLogDirsResponse_v0,
]
DescribeLogDirsRequest = [
    DescribeLogDirsRequest_v0,
]


class SaslAuthenticateResponse_v0(Response):
    API_KEY = 36
    API_VERSION = 0
    SCHEMA = Schema(
        ('error_code', Int16),
        ('error_message', String('utf-8')),
        ('sasl_auth_bytes', Bytes)
    )


class SaslAuthenticateResponse_v1(Response):
    API_KEY = 36
    API_VERSION = 1
    SCHEMA = Schema(
        ('error_code', Int16),
        ('error_message', String('utf-8')),
        ('sasl_auth_bytes', Bytes),
        ('session_lifetime_ms', Int64)
    )


class SaslAuthenticateRequest_v0(Request):
    API_KEY = 36
    API_VERSION = 0
    RESPONSE_TYPE = SaslAuthenticateResponse_v0
    SCHEMA = Schema(
        ('sasl_auth_bytes', Bytes)
    )


class SaslAuthenticateRequest_v1(Request):
    API_KEY = 36
    API_VERSION = 1
    RESPONSE_TYPE = SaslAuthenticateResponse_v1
    SCHEMA = SaslAuthenticateRequest_v0.SCHEMA


SaslAuthenticateRequest = [
    SaslAuthenticateRequest_v0, SaslAuthenticateRequest_v1,
]
SaslAuthenticateResponse = [
    SaslAuthenticateResponse_v0, SaslAuthenticateResponse_v1,
]


class CreatePartitionsResponse_v0(Response):
    API_KEY = 37
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('topic_errors', Array(
            ('topic', String('utf-8')),
            ('error_code', Int16),
            ('error_message', String('utf-8'))))
    )


class CreatePartitionsResponse_v1(Response):
    API_KEY = 37
    API_VERSION = 1
    SCHEMA = CreatePartitionsResponse_v0.SCHEMA


class CreatePartitionsRequest_v0(Request):
    API_KEY = 37
    API_VERSION = 0
    RESPONSE_TYPE = CreatePartitionsResponse_v0
    SCHEMA = Schema(
        ('topic_partitions', Array(
            ('topic', String('utf-8')),
            ('new_partitions', Schema(
                ('count', Int32),
                ('assignment', Array(Array(Int32))))))),
        ('timeout', Int32),
        ('validate_only', Boolean)
    )


class CreatePartitionsRequest_v1(Request):
    API_KEY = 37
    API_VERSION = 1
    SCHEMA = CreatePartitionsRequest_v0.SCHEMA
    RESPONSE_TYPE = CreatePartitionsResponse_v1


CreatePartitionsRequest = [
    CreatePartitionsRequest_v0, CreatePartitionsRequest_v1,
]
CreatePartitionsResponse = [
    CreatePartitionsResponse_v0, CreatePartitionsResponse_v1,
]


class DeleteGroupsResponse_v0(Response):
    API_KEY = 42
    API_VERSION = 0
    SCHEMA = Schema(
        ("throttle_time_ms", Int32),
        ("results", Array(
            ("group_id", String("utf-8")),
            ("error_code", Int16)))
    )


class DeleteGroupsResponse_v1(Response):
    API_KEY = 42
    API_VERSION = 1
    SCHEMA = DeleteGroupsResponse_v0.SCHEMA


class DeleteGroupsRequest_v0(Request):
    API_KEY = 42
    API_VERSION = 0
    RESPONSE_TYPE = DeleteGroupsResponse_v0
    SCHEMA = Schema(
        ("groups_names", Array(String("utf-8")))
    )


class DeleteGroupsRequest_v1(Request):
    API_KEY = 42
    API_VERSION = 1
    RESPONSE_TYPE = DeleteGroupsResponse_v1
    SCHEMA = DeleteGroupsRequest_v0.SCHEMA


DeleteGroupsRequest = [
    DeleteGroupsRequest_v0, DeleteGroupsRequest_v1
]

DeleteGroupsResponse = [
    DeleteGroupsResponse_v0, DeleteGroupsResponse_v1
]


class DescribeClientQuotasResponse_v0(Response):
    API_KEY = 48
    API_VERSION = 0
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('error_message', String('utf-8')),
        ('entries', Array(
            ('entity', Array(
                ('entity_type', String('utf-8')),
                ('entity_name', String('utf-8')))),
            ('values', Array(
                ('name', String('utf-8')),
                ('value', Float64))))),
    )


class DescribeClientQuotasRequest_v0(Request):
    API_KEY = 48
    API_VERSION = 0
    RESPONSE_TYPE = DescribeClientQuotasResponse_v0
    SCHEMA = Schema(
        ('components', Array(
            ('entity_type', String('utf-8')),
            ('match_type', Int8),
            ('match', String('utf-8')),
        )),
        ('strict', Boolean)
    )


DescribeClientQuotasRequest = [
    DescribeClientQuotasRequest_v0,
]

DescribeClientQuotasResponse = [
    DescribeClientQuotasResponse_v0,
]


class AlterPartitionReassignmentsResponse_v0(Response):
    API_KEY = 45
    API_VERSION = 0
    SCHEMA = Schema(
        ("throttle_time_ms", Int32),
        ("error_code", Int16),
        ("error_message", CompactString("utf-8")),
        ("responses", CompactArray(
            ("name", CompactString("utf-8")),
            ("partitions", CompactArray(
                ("partition_index", Int32),
                ("error_code", Int16),
                ("error_message", CompactString("utf-8")),
                ("tags", TaggedFields)
            )),
            ("tags", TaggedFields)
        )),
        ("tags", TaggedFields)
    )
    FLEXIBLE_VERSION = True


class AlterPartitionReassignmentsRequest_v0(Request):
    FLEXIBLE_VERSION = True
    API_KEY = 45
    API_VERSION = 0
    RESPONSE_TYPE = AlterPartitionReassignmentsResponse_v0
    SCHEMA = Schema(
        ("timeout_ms", Int32),
        ("topics", CompactArray(
            ("name", CompactString("utf-8")),
            ("partitions", CompactArray(
                ("partition_index", Int32),
                ("replicas", CompactArray(Int32)),
                ("tags", TaggedFields)
            )),
            ("tags", TaggedFields)
        )),
        ("tags", TaggedFields)
    )


AlterPartitionReassignmentsRequest = [AlterPartitionReassignmentsRequest_v0]

AlterPartitionReassignmentsResponse = [AlterPartitionReassignmentsResponse_v0]


class ListPartitionReassignmentsResponse_v0(Response):
    API_KEY = 46
    API_VERSION = 0
    SCHEMA = Schema(
        ("throttle_time_ms", Int32),
        ("error_code", Int16),
        ("error_message", CompactString("utf-8")),
        ("topics", CompactArray(
            ("name", CompactString("utf-8")),
            ("partitions", CompactArray(
                ("partition_index", Int32),
                ("replicas", CompactArray(Int32)),
                ("adding_replicas", CompactArray(Int32)),
                ("removing_replicas", CompactArray(Int32)),
                ("tags", TaggedFields)
            )),
            ("tags", TaggedFields)
        )),
        ("tags", TaggedFields)
    )
    FLEXIBLE_VERSION = True


class ListPartitionReassignmentsRequest_v0(Request):
    FLEXIBLE_VERSION = True
    API_KEY = 46
    API_VERSION = 0
    RESPONSE_TYPE = ListPartitionReassignmentsResponse_v0
    SCHEMA = Schema(
        ("timeout_ms", Int32),
        ("topics", CompactArray(
            ("name", CompactString("utf-8")),
            ("partition_index", CompactArray(Int32)),
            ("tags", TaggedFields)
        )),
        ("tags", TaggedFields)
    )


ListPartitionReassignmentsRequest = [ListPartitionReassignmentsRequest_v0]

ListPartitionReassignmentsResponse = [ListPartitionReassignmentsResponse_v0]


class ElectLeadersResponse_v0(Response):
    API_KEY = 43
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('replication_election_results', Array(
            ('topic', String('utf-8')),
            ('partition_result', Array(
                ('partition_id', Int32),
                ('error_code', Int16),
                ('error_message', String('utf-8'))
            ))
        ))
    )


class ElectLeadersRequest_v0(Request):
    API_KEY = 43
    API_VERSION = 1
    RESPONSE_TYPE = ElectLeadersResponse_v0
    SCHEMA = Schema(
        ('election_type', Int8),
        ('topic_partitions', Array(
            ('topic', String('utf-8')),
            ('partition_ids', Array(Int32))
        )),
        ('timeout', Int32),
    )


class ElectLeadersResponse_v1(Response):
    API_KEY = 43
    API_VERSION = 1
    SCHEMA = Schema(
        ('throttle_time_ms', Int32),
        ('error_code', Int16),
        ('replication_election_results', Array(
            ('topic', String('utf-8')),
            ('partition_result', Array(
                ('partition_id', Int32),
                ('error_code', Int16),
                ('error_message', String('utf-8'))
            ))
        ))
    )


class ElectLeadersRequest_v1(Request):
    API_KEY = 43
    API_VERSION = 1
    RESPONSE_TYPE = ElectLeadersResponse_v1
    SCHEMA = Schema(
        ('election_type', Int8),
        ('topic_partitions', Array(
            ('topic', String('utf-8')),
            ('partition_ids', Array(Int32))
        )),
        ('timeout', Int32),
    )


class ElectionType(IntEnum):
    """ Leader election type
    """

    PREFERRED = 0,
    UNCLEAN = 1


ElectLeadersRequest = [ElectLeadersRequest_v0, ElectLeadersRequest_v1]
ElectLeadersResponse = [ElectLeadersResponse_v0, ElectLeadersResponse_v1]
