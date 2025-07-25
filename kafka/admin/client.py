from __future__ import absolute_import, division

from collections import defaultdict
import copy
import itertools
import logging
import socket
import time

from . import ConfigResourceType
from kafka.vendor import six

from kafka.admin.acl_resource import ACLOperation, ACLPermissionType, ACLFilter, ACL, ResourcePattern, ResourceType, \
    ACLResourcePatternType, valid_acl_operations
from kafka.client_async import KafkaClient, selectors
from kafka.coordinator.protocol import ConsumerProtocolMemberMetadata_v0, ConsumerProtocolMemberAssignment_v0, ConsumerProtocol_v0
import kafka.errors as Errors
from kafka.errors import (
    IncompatibleBrokerVersion, KafkaConfigurationError, UnknownTopicOrPartitionError,
    UnrecognizedBrokerVersion, IllegalArgumentError)
from kafka.future import Future
from kafka.metrics import MetricConfig, Metrics
from kafka.protocol.admin import (
    CreateTopicsRequest, DeleteTopicsRequest, DescribeConfigsRequest, AlterConfigsRequest, CreatePartitionsRequest,
    ListGroupsRequest, DescribeGroupsRequest, DescribeAclsRequest, CreateAclsRequest, DeleteAclsRequest,
    DeleteGroupsRequest, DeleteRecordsRequest, DescribeLogDirsRequest, ElectLeadersRequest, ElectionType)
from kafka.protocol.commit import OffsetFetchRequest
from kafka.protocol.find_coordinator import FindCoordinatorRequest
from kafka.protocol.metadata import MetadataRequest
from kafka.protocol.types import Array
from kafka.structs import TopicPartition, OffsetAndMetadata, MemberInformation, GroupInformation
from kafka.version import __version__


log = logging.getLogger(__name__)


class KafkaAdminClient(object):
    """A class for administering the Kafka cluster.

    Warning:
        This is an unstable interface that was recently added and is subject to
        change without warning. In particular, many methods currently return
        raw protocol tuples. In future releases, we plan to make these into
        nicer, more pythonic objects. Unfortunately, this will likely break
        those interfaces.

    The KafkaAdminClient class will negotiate for the latest version of each message
    protocol format supported by both the kafka-python client library and the
    Kafka broker. Usage of optional fields from protocol versions that are not
    supported by the broker will result in IncompatibleBrokerVersion exceptions.

    Use of this class requires a minimum broker version >= 0.10.0.0.

    Keyword Arguments:
        bootstrap_servers: 'host[:port]' string (or list of 'host[:port]'
            strings) that the consumer should contact to bootstrap initial
            cluster metadata. This does not have to be the full node list.
            It just needs to have at least one broker that will respond to a
            Metadata API Request. Default port is 9092. If no servers are
            specified, will default to localhost:9092.
        client_id (str): a name for this client. This string is passed in
            each request to servers and can be used to identify specific
            server-side log entries that correspond to this client. Also
            submitted to GroupCoordinator for logging with respect to
            consumer group administration. Default: 'kafka-python-{version}'
        reconnect_backoff_ms (int): The amount of time in milliseconds to
            wait before attempting to reconnect to a given host.
            Default: 50.
        reconnect_backoff_max_ms (int): The maximum amount of time in
            milliseconds to backoff/wait when reconnecting to a broker that has
            repeatedly failed to connect. If provided, the backoff per host
            will increase exponentially for each consecutive connection
            failure, up to this maximum. Once the maximum is reached,
            reconnection attempts will continue periodically with this fixed
            rate. To avoid connection storms, a randomization factor of 0.2
            will be applied to the backoff resulting in a random range between
            20% below and 20% above the computed value. Default: 30000.
        request_timeout_ms (int): Client request timeout in milliseconds.
            Default: 30000.
        connections_max_idle_ms: Close idle connections after the number of
            milliseconds specified by this config. The broker closes idle
            connections after connections.max.idle.ms, so this avoids hitting
            unexpected socket disconnected errors on the client.
            Default: 540000
        retry_backoff_ms (int): Milliseconds to backoff when retrying on
            errors. Default: 100.
        max_in_flight_requests_per_connection (int): Requests are pipelined
            to kafka brokers up to this number of maximum requests per
            broker connection. Default: 5.
        receive_buffer_bytes (int): The size of the TCP receive buffer
            (SO_RCVBUF) to use when reading data. Default: None (relies on
            system defaults). Java client defaults to 32768.
        send_buffer_bytes (int): The size of the TCP send buffer
            (SO_SNDBUF) to use when sending data. Default: None (relies on
            system defaults). Java client defaults to 131072.
        socket_options (list): List of tuple-arguments to socket.setsockopt
            to apply to broker connection sockets. Default:
            [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)]
        metadata_max_age_ms (int): The period of time in milliseconds after
            which we force a refresh of metadata even if we haven't seen any
            partition leadership changes to proactively discover any new
            brokers or partitions. Default: 300000
        security_protocol (str): Protocol used to communicate with brokers.
            Valid values are: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL.
            Default: PLAINTEXT.
        ssl_context (ssl.SSLContext): Pre-configured SSLContext for wrapping
            socket connections. If provided, all other ssl_* configurations
            will be ignored. Default: None.
        ssl_check_hostname (bool): Flag to configure whether SSL handshake
            should verify that the certificate matches the broker's hostname.
            Default: True.
        ssl_cafile (str): Optional filename of CA file to use in certificate
            verification. Default: None.
        ssl_certfile (str): Optional filename of file in PEM format containing
            the client certificate, as well as any CA certificates needed to
            establish the certificate's authenticity. Default: None.
        ssl_keyfile (str): Optional filename containing the client private key.
            Default: None.
        ssl_password (str): Optional password to be used when loading the
            certificate chain. Default: None.
        ssl_crlfile (str): Optional filename containing the CRL to check for
            certificate expiration. By default, no CRL check is done. When
            providing a file, only the leaf certificate will be checked against
            this CRL. The CRL can only be checked with Python 3.4+ or 2.7.9+.
            Default: None.
        api_version (tuple): Specify which Kafka API version to use. If set
            to None, KafkaClient will attempt to infer the broker version by
            probing various APIs. Example: (0, 10, 2). Default: None
        api_version_auto_timeout_ms (int): number of milliseconds to throw a
            timeout exception from the constructor when checking the broker
            api version. Only applies if api_version is None
        selector (selectors.BaseSelector): Provide a specific selector
            implementation to use for I/O multiplexing.
            Default: selectors.DefaultSelector
        metrics (kafka.metrics.Metrics): Optionally provide a metrics
            instance for capturing network IO stats. Default: None.
        metric_group_prefix (str): Prefix for metric names. Default: ''
        sasl_mechanism (str): Authentication mechanism when security_protocol
            is configured for SASL_PLAINTEXT or SASL_SSL. Valid values are:
            PLAIN, GSSAPI, OAUTHBEARER, SCRAM-SHA-256, SCRAM-SHA-512.
        sasl_plain_username (str): username for sasl PLAIN and SCRAM authentication.
            Required if sasl_mechanism is PLAIN or one of the SCRAM mechanisms.
        sasl_plain_password (str): password for sasl PLAIN and SCRAM authentication.
            Required if sasl_mechanism is PLAIN or one of the SCRAM mechanisms.
        sasl_kerberos_name (str or gssapi.Name): Constructed gssapi.Name for use with
            sasl mechanism handshake. If provided, sasl_kerberos_service_name and
            sasl_kerberos_domain name are ignored. Default: None.
        sasl_kerberos_service_name (str): Service name to include in GSSAPI
            sasl mechanism handshake. Default: 'kafka'
        sasl_kerberos_domain_name (str): kerberos domain name to use in GSSAPI
            sasl mechanism handshake. Default: one of bootstrap servers
        sasl_oauth_token_provider (kafka.sasl.oauth.AbstractTokenProvider): OAuthBearer
            token provider instance. Default: None
        socks5_proxy (str): Socks5 proxy url. Default: None
        kafka_client (callable): Custom class / callable for creating KafkaClient instances
    """
    DEFAULT_CONFIG = {
        # client configs
        'bootstrap_servers': 'localhost',
        'client_id': 'kafka-python-' + __version__,
        'request_timeout_ms': 30000,
        'connections_max_idle_ms': 9 * 60 * 1000,
        'reconnect_backoff_ms': 50,
        'reconnect_backoff_max_ms': 30000,
        'max_in_flight_requests_per_connection': 5,
        'receive_buffer_bytes': None,
        'send_buffer_bytes': None,
        'socket_options': [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)],
        'sock_chunk_bytes': 4096,  # undocumented experimental option
        'sock_chunk_buffer_count': 1000,  # undocumented experimental option
        'retry_backoff_ms': 100,
        'metadata_max_age_ms': 300000,
        'security_protocol': 'PLAINTEXT',
        'ssl_context': None,
        'ssl_check_hostname': True,
        'ssl_cafile': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
        'ssl_password': None,
        'ssl_crlfile': None,
        'api_version': None,
        'api_version_auto_timeout_ms': 2000,
        'selector': selectors.DefaultSelector,
        'sasl_mechanism': None,
        'sasl_plain_username': None,
        'sasl_plain_password': None,
        'sasl_kerberos_name': None,
        'sasl_kerberos_service_name': 'kafka',
        'sasl_kerberos_domain_name': None,
        'sasl_oauth_token_provider': None,
        'socks5_proxy': None,

        # metrics configs
        'metric_reporters': [],
        'metrics_num_samples': 2,
        'metrics_sample_window_ms': 30000,
        'kafka_client': KafkaClient,
    }

    def __init__(self, **configs):
        log.debug("Starting KafkaAdminClient with configuration: %s", configs)
        extra_configs = set(configs).difference(self.DEFAULT_CONFIG)
        if extra_configs:
            raise KafkaConfigurationError("Unrecognized configs: {}".format(extra_configs))

        self.config = copy.copy(self.DEFAULT_CONFIG)
        self.config.update(configs)

        # Configure metrics
        metrics_tags = {'client-id': self.config['client_id']}
        metric_config = MetricConfig(samples=self.config['metrics_num_samples'],
                                     time_window_ms=self.config['metrics_sample_window_ms'],
                                     tags=metrics_tags)
        reporters = [reporter() for reporter in self.config['metric_reporters']]
        self._metrics = Metrics(metric_config, reporters)

        self._client = self.config['kafka_client'](
            metrics=self._metrics,
            metric_group_prefix='admin',
            **self.config
        )

        # Get auto-discovered version from client if necessary
        self.config['api_version'] = self._client.config['api_version']

        self._closed = False
        self._refresh_controller_id()
        log.debug("KafkaAdminClient started.")

    def close(self):
        """Close the KafkaAdminClient connection to the Kafka broker."""
        if not hasattr(self, '_closed') or self._closed:
            log.info("KafkaAdminClient already closed.")
            return

        self._metrics.close()
        self._client.close()
        self._closed = True
        log.debug("KafkaAdminClient is now closed.")

    def _validate_timeout(self, timeout_ms):
        """Validate the timeout is set or use the configuration default.

        Arguments:
            timeout_ms: The timeout provided by api call, in milliseconds.

        Returns:
            The timeout to use for the operation.
        """
        return timeout_ms or self.config['request_timeout_ms']

    def _refresh_controller_id(self, timeout_ms=30000):
        """Determine the Kafka cluster controller."""
        version = self._client.api_version(MetadataRequest, max_version=8)
        if version == 0:
            raise UnrecognizedBrokerVersion(
                "Kafka Admin interface cannot determine the controller using MetadataRequest_v{}."
                .format(version))
        # use defaults for allow_auto_topic_creation / include_authorized_operations in v6+
        request = MetadataRequest[version]()

        timeout_at = time.time() + timeout_ms / 1000
        while time.time() < timeout_at:
            response = self.send_request(request)
            controller_id = response.controller_id
            if controller_id == -1:
                log.warning("Controller ID not available, got -1")
                time.sleep(1)
                continue
            # verify the controller is new enough to support our requests
            controller_version = self._client.check_version(node_id=controller_id)
            if controller_version < (0, 10, 0):
                raise IncompatibleBrokerVersion(
                    "The controller appears to be running Kafka {}. KafkaAdminClient requires brokers >= 0.10.0.0."
                    .format(controller_version))
            self._controller_id = controller_id
            return
        else:
            raise Errors.NodeNotReadyError('controller')

    def _find_coordinator_id_request(self, group_id):
        """Send a FindCoordinatorRequest to a broker.

        Arguments:
            group_id: The consumer group ID. This is typically the group
            name as a string.

        Returns:
            FindCoordinatorRequest
        """
        version = self._client.api_version(FindCoordinatorRequest, max_version=2)
        if version <= 0:
            request = FindCoordinatorRequest[version](group_id)
        elif version <= 2:
            request = FindCoordinatorRequest[version](group_id, 0)
        return request

    def _find_coordinator_id_process_response(self, response):
        """Process a FindCoordinatorResponse.

        Arguments:
            response: a FindCoordinatorResponse.

        Returns:
            The node_id of the broker that is the coordinator.
        """
        error_type = Errors.for_code(response.error_code)
        if error_type is not Errors.NoError:
            # Note: When error_type.retriable, Java will retry... see
            # KafkaAdminClient's handleFindCoordinatorError method
            raise error_type(
                "FindCoordinatorRequest failed with response '{}'."
                .format(response))
        return response.coordinator_id

    def _find_coordinator_ids(self, group_ids):
        """Find the broker node_ids of the coordinators of the given groups.

        Sends a FindCoordinatorRequest message to the cluster for each group_id.
        Will block until the FindCoordinatorResponse is received for all groups.
        Any errors are immediately raised.

        Arguments:
            group_ids: A list of consumer group IDs. This is typically the group
            name as a string.

        Returns:
            A dict of {group_id: node_id} where node_id is the id of the
            broker that is the coordinator for the corresponding group.
        """
        requests = [(self._find_coordinator_id_request(group_id), None) for group_id in group_ids]
        coordinator_ids = self.send_requests(requests, response_fn=self._find_coordinator_id_process_response)
        return dict(zip(group_ids, coordinator_ids))

    def _send_request_to_node(self, node_id, request, wakeup=True):
        """Send a Kafka protocol message to a specific broker.

        Arguments:
            node_id: The broker id to which to send the message.
            request: The message to send.


        Keyword Arguments:
            wakeup (bool, optional): Optional flag to disable thread-wakeup.

        Returns:
            A future object that may be polled for status and results.
        """
        try:
            self._client.await_ready(node_id)
        except Errors.KafkaConnectionError as e:
            return Future().failure(e)
        return self._client.send(node_id, request, wakeup)

    def _wait_for_futures(self, futures):
        """Block until all futures complete. If any fail, raise the encountered exception.

        Arguments:
            futures: A list of Future objects awaiting results.

        Raises:
            The first encountered exception if a future fails.
        """
        while not all(future.succeeded() for future in futures):
            for future in futures:
                self._client.poll(future=future)

                if future.failed():
                    raise future.exception  # pylint: disable-msg=raising-bad-type

    def send_request(self, request, node_id=None):
        if node_id is None:
            node_id = self._client.least_loaded_node()
        self._client.await_ready(node_id)
        future = self._client.send(node_id, request)
        self._wait_for_futures([future]) # raises exception on failure
        return future.value

    def send_requests(self, requests_and_node_ids, response_fn=lambda x: x):
        futures = []
        for request, node_id in requests_and_node_ids:
            if node_id is None:
                node_id = self._client.least_loaded_node()
            self._client.await_ready(node_id)
            futures.append(self._client.send(node_id, request))
        self._wait_for_futures(futures)
        return [response_fn(future.value) for future in futures]

    def _send_request_to_controller(self, request):
        """Send a Kafka protocol message to the cluster controller.

        Will block until the message result is received.

        Arguments:
            request: The message to send.

        Returns:
            The Kafka protocol response for the message.
        """
        tries = 2  # in case our cached self._controller_id is outdated
        while tries:
            tries -= 1
            response = self.send_request(request, node_id=self._controller_id)
            # In Java, the error field name is inconsistent:
            #  - CreateTopicsResponse / CreatePartitionsResponse uses topic_errors
            #  - DeleteTopicsResponse uses topic_error_codes
            # So this is a little brittle in that it assumes all responses have
            # one of these attributes and that they always unpack into
            # (topic, error_code) tuples.
            topic_error_tuples = getattr(response, 'topic_errors', getattr(response, 'topic_error_codes', None))
            if topic_error_tuples is not None:
                success = self._parse_topic_request_response(topic_error_tuples, request, response, tries)
            else:
                # Leader Election request has a two layer error response (topic and partition)
                success = self._parse_topic_partition_request_response(request, response, tries)

            if success:
                return response
        raise RuntimeError("This should never happen, please file a bug with full stacktrace if encountered")

    def _parse_topic_request_response(self, topic_error_tuples, request, response, tries):
        # Also small py2/py3 compatibility -- py3 can ignore extra values
        # during unpack via: for x, y, *rest in list_of_values. py2 cannot.
        # So for now we have to map across the list and explicitly drop any
        # extra values (usually the error_message)
        for topic, error_code in map(lambda e: e[:2], topic_error_tuples):
            error_type = Errors.for_code(error_code)
            if tries and error_type is Errors.NotControllerError:
                # No need to inspect the rest of the errors for
                # non-retriable errors because NotControllerError should
                # either be thrown for all errors or no errors.
                self._refresh_controller_id()
                return False
            elif error_type is not Errors.NoError:
                raise error_type(
                    "Request '{}' failed with response '{}'."
                    .format(request, response))
        return True

    def _parse_topic_partition_request_response(self, request, response, tries):
        # Also small py2/py3 compatibility -- py3 can ignore extra values
        # during unpack via: for x, y, *rest in list_of_values. py2 cannot.
        # So for now we have to map across the list and explicitly drop any
        # extra values (usually the error_message)
        for topic, partition_results in response.replication_election_results:
            for partition_id, error_code in map(lambda e: e[:2], partition_results):
                error_type = Errors.for_code(error_code)
                if tries and error_type is Errors.NotControllerError:
                    # No need to inspect the rest of the errors for
                    # non-retriable errors because NotControllerError should
                    # either be thrown for all errors or no errors.
                    self._refresh_controller_id()
                    return False
                elif error_type not in (Errors.NoError, Errors.ElectionNotNeededError):
                    raise error_type(
                        "Request '{}' failed with response '{}'."
                        .format(request, response))
        return True

    @staticmethod
    def _convert_new_topic_request(new_topic):
        """
        Build the tuple required by CreateTopicsRequest from a NewTopic object.

        Arguments:
            new_topic: A NewTopic instance containing name, partition count, replication factor,
                          replica assignments, and config entries.

        Returns:
            A tuple in the form:
                 (topic_name, num_partitions, replication_factor, [(partition_id, [replicas])...],
                  [(config_key, config_value)...])
        """
        return (
            new_topic.name,
            new_topic.num_partitions,
            new_topic.replication_factor,
            [
                (partition_id, replicas) for partition_id, replicas in new_topic.replica_assignments.items()
            ],
            [
                (config_key, config_value) for config_key, config_value in new_topic.topic_configs.items()
            ]
        )

    def create_topics(self, new_topics, timeout_ms=None, validate_only=False):
        """Create new topics in the cluster.

        Arguments:
            new_topics: A list of NewTopic objects.

        Keyword Arguments:
            timeout_ms (numeric, optional): Milliseconds to wait for new topics to be created
                before the broker returns.
            validate_only (bool, optional): If True, don't actually create new topics.
                Not supported by all versions. Default: False

        Returns:
            Appropriate version of CreateTopicResponse class.
        """
        version = self._client.api_version(CreateTopicsRequest, max_version=3)
        timeout_ms = self._validate_timeout(timeout_ms)
        if version == 0:
            if validate_only:
                raise IncompatibleBrokerVersion(
                    "validate_only requires CreateTopicsRequest >= v1, which is not supported by Kafka {}."
                    .format(self.config['api_version']))
            request = CreateTopicsRequest[version](
                create_topic_requests=[self._convert_new_topic_request(new_topic) for new_topic in new_topics],
                timeout=timeout_ms
            )
        elif version <= 3:
            request = CreateTopicsRequest[version](
                create_topic_requests=[self._convert_new_topic_request(new_topic) for new_topic in new_topics],
                timeout=timeout_ms,
                validate_only=validate_only
            )
        # TODO convert structs to a more pythonic interface
        # TODO raise exceptions if errors
        return self._send_request_to_controller(request)

    def delete_topics(self, topics, timeout_ms=None):
        """Delete topics from the cluster.

        Arguments:
            topics ([str]): A list of topic name strings.

        Keyword Arguments:
            timeout_ms (numeric, optional): Milliseconds to wait for topics to be deleted
                before the broker returns.

        Returns:
            Appropriate version of DeleteTopicsResponse class.
        """
        version = self._client.api_version(DeleteTopicsRequest, max_version=3)
        timeout_ms = self._validate_timeout(timeout_ms)
        return self._send_request_to_controller(
            DeleteTopicsRequest[version](
                topics=topics,
                timeout=timeout_ms
            )
        )

    def _process_metadata_response(self, metadata_response):
        obj = metadata_response.to_object()
        if 'authorized_operations' in obj:
            obj['authorized_operations'] = list(map(lambda acl: acl.name, valid_acl_operations(obj['authorized_operations'])))
        for t in obj['topics']:
            if 'authorized_operations' in t:
                t['authorized_operations'] = list(map(lambda acl: acl.name, valid_acl_operations(t['authorized_operations'])))
        return obj

    def _get_cluster_metadata(self, topics=None, auto_topic_creation=False):
        """
        topics == None means "get all topics"
        """
        version = self._client.api_version(MetadataRequest, max_version=8)
        if version <= 3:
            if auto_topic_creation:
                raise IncompatibleBrokerVersion(
                    "auto_topic_creation requires MetadataRequest >= v4, which"
                    " is not supported by Kafka {}"
                    .format(self.config['api_version']))

            request = MetadataRequest[version](topics=topics)
        elif version <= 7:
            request = MetadataRequest[version](
                topics=topics,
                allow_auto_topic_creation=auto_topic_creation
            )
        else:
            request = MetadataRequest[version](
                topics=topics,
                allow_auto_topic_creation=auto_topic_creation,
                include_cluster_authorized_operations=True,
                include_topic_authorized_operations=True,
            )

        return self._process_metadata_response(self.send_request(request))

    def list_topics(self):
        """Retrieve a list of all topic names in the cluster.

        Returns:
            A list of topic name strings.
        """
        metadata = self._get_cluster_metadata(topics=None)
        return [t['topic'] for t in metadata['topics']]

    def describe_topics(self, topics=None):
        """Fetch metadata for the specified topics or all topics if None.

        Keyword Arguments:
            topics ([str], optional) A list of topic names. If None, metadata for all
                topics is retrieved.

        Returns:
            A list of dicts describing each topic (including partition info).
        """
        metadata = self._get_cluster_metadata(topics=topics)
        return metadata['topics']

    def describe_cluster(self):
        """
        Fetch cluster-wide metadata such as the list of brokers, the controller ID,
        and the cluster ID.


        Returns:
            A dict with cluster-wide metadata, excluding topic details.
        """
        metadata = self._get_cluster_metadata()
        metadata.pop('topics')  # We have 'describe_topics' for this
        return metadata

    @staticmethod
    def _convert_describe_acls_response_to_acls(describe_response):
        """Convert a DescribeAclsResponse into a list of ACL objects and a KafkaError.

        Arguments:
            describe_response: The response object from the DescribeAclsRequest.

        Returns:
            A tuple of (list_of_acl_objects, error) where error is an instance
                 of KafkaError (NoError if successful).
        """
        version = describe_response.API_VERSION

        error = Errors.for_code(describe_response.error_code)
        acl_list = []
        for resources in describe_response.resources:
            if version == 0:
                resource_type, resource_name, acls = resources
                resource_pattern_type = ACLResourcePatternType.LITERAL.value
            elif version <= 1:
                resource_type, resource_name, resource_pattern_type, acls = resources
            else:
                raise NotImplementedError(
                    "Support for DescribeAcls Response v{} has not yet been added to KafkaAdmin."
                        .format(version)
                )
            for acl in acls:
                principal, host, operation, permission_type = acl
                conv_acl = ACL(
                    principal=principal,
                    host=host,
                    operation=ACLOperation(operation),
                    permission_type=ACLPermissionType(permission_type),
                    resource_pattern=ResourcePattern(
                        ResourceType(resource_type),
                        resource_name,
                        ACLResourcePatternType(resource_pattern_type)
                    )
                )
                acl_list.append(conv_acl)

        return (acl_list, error,)

    def describe_acls(self, acl_filter):
        """Describe a set of ACLs

        Used to return a set of ACLs matching the supplied ACLFilter.
        The cluster must be configured with an authorizer for this to work, or
        you will get a SecurityDisabledError

        Arguments:
            acl_filter: an ACLFilter object

        Returns:
            tuple of a list of matching ACL objects and a KafkaError (NoError if successful)
        """

        version = self._client.api_version(DescribeAclsRequest, max_version=1)
        if version == 0:
            request = DescribeAclsRequest[version](
                resource_type=acl_filter.resource_pattern.resource_type,
                resource_name=acl_filter.resource_pattern.resource_name,
                principal=acl_filter.principal,
                host=acl_filter.host,
                operation=acl_filter.operation,
                permission_type=acl_filter.permission_type
            )
        elif version <= 1:
            request = DescribeAclsRequest[version](
                resource_type=acl_filter.resource_pattern.resource_type,
                resource_name=acl_filter.resource_pattern.resource_name,
                resource_pattern_type_filter=acl_filter.resource_pattern.pattern_type,
                principal=acl_filter.principal,
                host=acl_filter.host,
                operation=acl_filter.operation,
                permission_type=acl_filter.permission_type

            )
        response = self.send_request(request)
        error_type = Errors.for_code(response.error_code)
        if error_type is not Errors.NoError:
            # optionally we could retry if error_type.retriable
            raise error_type(
                "Request '{}' failed with response '{}'."
                    .format(request, response))

        return self._convert_describe_acls_response_to_acls(response)

    @staticmethod
    def _convert_create_acls_resource_request_v0(acl):
        """Convert an ACL object into the CreateAclsRequest v0 format.

        Arguments:
            acl: An ACL object with resource pattern and permissions.

        Returns:
            A tuple: (resource_type, resource_name, principal, host, operation, permission_type).
        """

        return (
            acl.resource_pattern.resource_type,
            acl.resource_pattern.resource_name,
            acl.principal,
            acl.host,
            acl.operation,
            acl.permission_type
        )

    @staticmethod
    def _convert_create_acls_resource_request_v1(acl):
        """Convert an ACL object into the CreateAclsRequest v1 format.

        Arguments:
            acl: An ACL object with resource pattern and permissions.

        Returns:
            A tuple: (resource_type, resource_name, pattern_type, principal, host, operation, permission_type).
        """
        return (
            acl.resource_pattern.resource_type,
            acl.resource_pattern.resource_name,
            acl.resource_pattern.pattern_type,
            acl.principal,
            acl.host,
            acl.operation,
            acl.permission_type
        )

    @staticmethod
    def _convert_create_acls_response_to_acls(acls, create_response):
        """Parse CreateAclsResponse and correlate success/failure with original ACL objects.

        Arguments:
            acls: A list of ACL objects that were requested for creation.
            create_response: The broker's CreateAclsResponse object.

        Returns:
            A dict with:
                 {
                   'succeeded': [list of ACL objects successfully created],
                   'failed': [(acl_object, KafkaError), ...]
                 }
        """
        version = create_response.API_VERSION

        creations_error = []
        creations_success = []
        for i, creations in enumerate(create_response.creation_responses):
            if version <= 1:
                error_code, error_message = creations
                acl = acls[i]
                error = Errors.for_code(error_code)
            else:
                raise NotImplementedError(
                    "Support for DescribeAcls Response v{} has not yet been added to KafkaAdmin."
                        .format(version)
                )

            if error is Errors.NoError:
                creations_success.append(acl)
            else:
                creations_error.append((acl, error,))

        return {"succeeded": creations_success, "failed": creations_error}

    def create_acls(self, acls):
        """Create a list of ACLs

        This endpoint only accepts a list of concrete ACL objects, no ACLFilters.
        Throws TopicAlreadyExistsError if topic is already present.

        Arguments:
            acls: a list of ACL objects

        Returns:
            dict of successes and failures
        """

        for acl in acls:
            if not isinstance(acl, ACL):
                raise IllegalArgumentError("acls must contain ACL objects")

        version = self._client.api_version(CreateAclsRequest, max_version=1)
        if version == 0:
            request = CreateAclsRequest[version](
                creations=[self._convert_create_acls_resource_request_v0(acl) for acl in acls]
            )
        elif version <= 1:
            request = CreateAclsRequest[version](
                creations=[self._convert_create_acls_resource_request_v1(acl) for acl in acls]
            )
        response = self.send_request(request)
        return self._convert_create_acls_response_to_acls(acls, response)

    @staticmethod
    def _convert_delete_acls_resource_request_v0(acl):
        """Convert an ACLFilter object into the DeleteAclsRequest v0 format.

        Arguments:
            acl: An ACLFilter object identifying the ACLs to be deleted.

        Returns:
            A tuple: (resource_type, resource_name, principal, host, operation, permission_type).
        """
        return (
            acl.resource_pattern.resource_type,
            acl.resource_pattern.resource_name,
            acl.principal,
            acl.host,
            acl.operation,
            acl.permission_type
        )

    @staticmethod
    def _convert_delete_acls_resource_request_v1(acl):
        """Convert an ACLFilter object into the DeleteAclsRequest v1 format.

        Arguments:
            acl: An ACLFilter object identifying the ACLs to be deleted.

        Returns:
            A tuple: (resource_type, resource_name, pattern_type, principal, host, operation, permission_type).
        """
        return (
            acl.resource_pattern.resource_type,
            acl.resource_pattern.resource_name,
            acl.resource_pattern.pattern_type,
            acl.principal,
            acl.host,
            acl.operation,
            acl.permission_type
        )

    @staticmethod
    def _convert_delete_acls_response_to_matching_acls(acl_filters, delete_response):
        """Parse the DeleteAclsResponse and map the results back to each input ACLFilter.

        Arguments:
            acl_filters: A list of ACLFilter objects that were provided in the request.
            delete_response: The response from the DeleteAclsRequest.

        Returns:
            A list of tuples of the form:
                 (acl_filter, [(matching_acl, KafkaError), ...], filter_level_error).
        """
        version = delete_response.API_VERSION
        filter_result_list = []
        for i, filter_responses in enumerate(delete_response.filter_responses):
            filter_error_code, filter_error_message, matching_acls = filter_responses
            filter_error = Errors.for_code(filter_error_code)
            acl_result_list = []
            for acl in matching_acls:
                if version == 0:
                    error_code, error_message, resource_type, resource_name, principal, host, operation, permission_type = acl
                    resource_pattern_type = ACLResourcePatternType.LITERAL.value
                elif version == 1:
                    error_code, error_message, resource_type, resource_name, resource_pattern_type, principal, host, operation, permission_type = acl
                else:
                    raise NotImplementedError(
                        "Support for DescribeAcls Response v{} has not yet been added to KafkaAdmin."
                            .format(version)
                    )
                acl_error = Errors.for_code(error_code)
                conv_acl = ACL(
                    principal=principal,
                    host=host,
                    operation=ACLOperation(operation),
                    permission_type=ACLPermissionType(permission_type),
                    resource_pattern=ResourcePattern(
                        ResourceType(resource_type),
                        resource_name,
                        ACLResourcePatternType(resource_pattern_type)
                    )
                )
                acl_result_list.append((conv_acl, acl_error,))
            filter_result_list.append((acl_filters[i], acl_result_list, filter_error,))
        return filter_result_list

    def delete_acls(self, acl_filters):
        """Delete a set of ACLs

        Deletes all ACLs matching the list of input ACLFilter

        Arguments:
            acl_filters: a list of ACLFilter

        Returns:
            a list of 3-tuples corresponding to the list of input filters.
                 The tuples hold (the input ACLFilter, list of affected ACLs, KafkaError instance)
        """

        for acl in acl_filters:
            if not isinstance(acl, ACLFilter):
                raise IllegalArgumentError("acl_filters must contain ACLFilter type objects")

        version = self._client.api_version(DeleteAclsRequest, max_version=1)

        if version == 0:
            request = DeleteAclsRequest[version](
                filters=[self._convert_delete_acls_resource_request_v0(acl) for acl in acl_filters]
            )
        elif version <= 1:
            request = DeleteAclsRequest[version](
                filters=[self._convert_delete_acls_resource_request_v1(acl) for acl in acl_filters]
            )
        response = self.send_request(request)
        return self._convert_delete_acls_response_to_matching_acls(acl_filters, response)

    @staticmethod
    def _convert_describe_config_resource_request(config_resource):
        """Convert a ConfigResource into the format required by DescribeConfigsRequest.

        Arguments:
            config_resource: A ConfigResource with resource_type, name, and optional config keys.

        Returns:
            A tuple: (resource_type, resource_name, [list_of_config_keys] or None).
        """
        return (
            config_resource.resource_type,
            config_resource.name,
            [
                config_key for config_key, config_value in config_resource.configs.items()
            ] if config_resource.configs else None
        )

    def describe_configs(self, config_resources, include_synonyms=False):
        """Fetch configuration parameters for one or more Kafka resources.

        Arguments:
            config_resources: An list of ConfigResource objects.
                Any keys in ConfigResource.configs dict will be used to filter the
                result. Setting the configs dict to None will get all values. An
                empty dict will get zero values (as per Kafka protocol).

        Keyword Arguments:
            include_synonyms (bool, optional): If True, return synonyms in response. Not
                supported by all versions. Default: False.

        Returns:
            List of DescribeConfigsResponses.
        """

        # Break up requests by type - a broker config request must be sent to the specific broker.
        # All other (currently just topic resources) can be sent to any broker.
        broker_resources = []
        topic_resources = []

        for config_resource in config_resources:
            if config_resource.resource_type == ConfigResourceType.BROKER:
                broker_resources.append(self._convert_describe_config_resource_request(config_resource))
            else:
                topic_resources.append(self._convert_describe_config_resource_request(config_resource))

        version = self._client.api_version(DescribeConfigsRequest, max_version=2)
        if include_synonyms and version == 0:
            raise IncompatibleBrokerVersion(
                "include_synonyms requires DescribeConfigsRequest >= v1, which is not supported by Kafka {}."
                    .format(self.config['api_version']))

        requests = []
        if len(broker_resources) > 0:
            for broker_resource in broker_resources:
                try:
                    broker_id = int(broker_resource[1])
                except ValueError:
                    raise ValueError("Broker resource names must be an integer or a string represented integer")

                if version == 0:
                    request = DescribeConfigsRequest[version](resources=[broker_resource])
                else:
                    request = DescribeConfigsRequest[version](
                        resources=[broker_resource],
                        include_synonyms=include_synonyms)
                requests.append((request, broker_id))

        if len(topic_resources) > 0:
            if version == 0:
                request = DescribeConfigsRequest[version](resources=topic_resources)
            else:
                request = DescribeConfigsRequest[version](resources=topic_resources, include_synonyms=include_synonyms)
            requests.append((request, None))

        return self.send_requests(requests)

    @staticmethod
    def _convert_alter_config_resource_request(config_resource):
        """Convert a ConfigResource into the format required by AlterConfigsRequest.

        Arguments:
            config_resource: A ConfigResource with resource_type, name, and config (key, value) pairs.

        Returns:
            A tuple: (resource_type, resource_name, [(config_key, config_value), ...]).
        """
        return (
            config_resource.resource_type,
            config_resource.name,
            [
                (config_key, config_value) for config_key, config_value in config_resource.configs.items()
            ]
        )

    def alter_configs(self, config_resources):
        """Alter configuration parameters of one or more Kafka resources.

        Warning:
            This is currently broken for BROKER resources because those must be
            sent to that specific broker, versus this always picks the
            least-loaded node. See the comment in the source code for details.
            We would happily accept a PR fixing this.

        Arguments:
            config_resources: A list of ConfigResource objects.

        Returns:
            Appropriate version of AlterConfigsResponse class.
        """
        version = self._client.api_version(AlterConfigsRequest, max_version=1)
        request = AlterConfigsRequest[version](
            resources=[self._convert_alter_config_resource_request(config_resource) for config_resource in config_resources]
        )
        # TODO the Java client has the note:
        # // We must make a separate AlterConfigs request for every BROKER resource we want to alter
        # // and send the request to that specific broker. Other resources are grouped together into
        # // a single request that may be sent to any broker.
        #
        # So this is currently broken as it always sends to the least_loaded_node()
        return self.send_request(request)

    # alter replica logs dir protocol not yet implemented
    # Note: have to lookup the broker with the replica assignment and send the request to that broker

    # describe log dirs protocol not yet implemented
    # Note: have to lookup the broker with the replica assignment and send the request to that broker

    @staticmethod
    def _convert_create_partitions_request(topic_name, new_partitions):
        """Convert a NewPartitions object into the tuple format for CreatePartitionsRequest.

        Arguments:
            topic_name: The name of the existing topic.
            new_partitions: A NewPartitions instance with total_count and new_assignments.

        Returns:
            A tuple: (topic_name, (total_count, [list_of_assignments])).
        """
        return (
            topic_name,
            (
                new_partitions.total_count,
                new_partitions.new_assignments
            )
        )

    def create_partitions(self, topic_partitions, timeout_ms=None, validate_only=False):
        """Create additional partitions for an existing topic.

        Arguments:
            topic_partitions: A map of topic name strings to NewPartition objects.

        Keyword Arguments:
            timeout_ms (numeric, optional): Milliseconds to wait for new partitions to be
                created before the broker returns.
            validate_only (bool, optional): If True, don't actually create new partitions.
                Default: False

        Returns:
            Appropriate version of CreatePartitionsResponse class.
        """
        version = self._client.api_version(CreatePartitionsRequest, max_version=1)
        timeout_ms = self._validate_timeout(timeout_ms)
        request = CreatePartitionsRequest[version](
            topic_partitions=[self._convert_create_partitions_request(topic_name, new_partitions) for topic_name, new_partitions in topic_partitions.items()],
            timeout=timeout_ms,
            validate_only=validate_only
        )
        return self._send_request_to_controller(request)

    def _get_leader_for_partitions(self, partitions, timeout_ms=None):
        """Finds ID of the leader node for every given topic partition.

        Will raise UnknownTopicOrPartitionError if for some partition no leader can be found.

        :param partitions: ``[TopicPartition]``: partitions for which to find leaders.
        :param timeout_ms: ``float``: Timeout in milliseconds, if None (default), will be read from
            config.

        :return: Dictionary with ``{leader_id -> {partitions}}``
        """
        timeout_ms = self._validate_timeout(timeout_ms)

        partitions = set(partitions)
        topics = set(tp.topic for tp in partitions)

        metadata = self._get_cluster_metadata(topics=topics)

        leader2partitions = defaultdict(list)
        valid_partitions = set()
        for topic in metadata.get("topics", ()):
            for partition in topic.get("partitions", ()):
                t2p = TopicPartition(topic=topic["topic"], partition=partition["partition"])
                if t2p in partitions:
                    leader2partitions[partition["leader"]].append(t2p)
                    valid_partitions.add(t2p)

        if len(partitions) != len(valid_partitions):
            unknown = set(partitions) - valid_partitions
            raise UnknownTopicOrPartitionError(
                "The following partitions are not known: %s"
                % ", ".join(str(x) for x in unknown)
            )

        return leader2partitions

    def delete_records(self, records_to_delete, timeout_ms=None, partition_leader_id=None):
        """Delete records whose offset is smaller than the given offset of the corresponding partition.

        :param records_to_delete: ``{TopicPartition: int}``: The earliest available offsets for the
            given partitions.
        :param timeout_ms: ``float``: Timeout in milliseconds, if None (default), will be read from
            config.
        :param partition_leader_id: ``str``: If specified, all deletion requests will be sent to
            this node. No check is performed verifying that this is indeed the leader for all
            listed partitions: use with caution.

        :return: Dictionary {topicPartition -> metadata}, where metadata is returned by the broker.
            See DeleteRecordsResponse for possible fields. error_code for all partitions is
            guaranteed to be zero, otherwise an exception is raised.
        """
        timeout_ms = self._validate_timeout(timeout_ms)
        responses = []
        version = self._client.api_version(DeleteRecordsRequest, max_version=0)

        # We want to make as few requests as possible
        # If a single node serves as a partition leader for multiple partitions (and/or
        # topics), we can send all of those in a single request.
        # For that we store {leader -> {partitions for leader}}, and do 1 request per leader
        if partition_leader_id is None:
            leader2partitions = self._get_leader_for_partitions(
                set(records_to_delete), timeout_ms
            )
        else:
            leader2partitions = {partition_leader_id: set(records_to_delete)}

        for leader, partitions in leader2partitions.items():
            topic2partitions = defaultdict(list)
            for partition in partitions:
                topic2partitions[partition.topic].append(partition)

            request = DeleteRecordsRequest[version](
                topics=[
                    (topic, [(tp.partition, records_to_delete[tp]) for tp in partitions])
                    for topic, partitions in topic2partitions.items()
                ],
                timeout_ms=timeout_ms
            )
            response = self.send_request(request, node_id=leader)
            responses.append(response.to_object())

        partition2result = {}
        partition2error = {}
        for response in responses:
            for topic in response["topics"]:
                for partition in topic["partitions"]:
                    tp = TopicPartition(topic["name"], partition["partition_index"])
                    partition2result[tp] = partition
                    if partition["error_code"] != 0:
                        partition2error[tp] = partition["error_code"]

        if partition2error:
            if len(partition2error) == 1:
                key, error = next(iter(partition2error.items()))
                raise Errors.for_code(error)(
                    "Error deleting records from topic %s partition %s" % (key.topic, key.partition)
                )
            else:
                raise Errors.BrokerResponseError(
                    "The following errors occured when trying to delete records: " +
                    ", ".join(
                        "%s(partition=%d): %s" %
                        (partition.topic, partition.partition, Errors.for_code(error).__name__)
                        for partition, error in partition2error.items()
                    )
                )

        return partition2result

    # create delegation token protocol not yet implemented
    # Note: send the request to the least_loaded_node()

    # renew delegation token protocol not yet implemented
    # Note: send the request to the least_loaded_node()

    # expire delegation_token protocol not yet implemented
    # Note: send the request to the least_loaded_node()

    # describe delegation_token protocol not yet implemented
    # Note: send the request to the least_loaded_node()

    def _describe_consumer_groups_request(self, group_id):
        """Send a DescribeGroupsRequest to the group's coordinator.

        Arguments:
            group_id: The group name as a string

        Returns:
            DescribeGroupsRequest object
        """
        version = self._client.api_version(DescribeGroupsRequest, max_version=3)
        if version <= 2:
            # Note: KAFKA-6788 A potential optimization is to group the
            # request per coordinator and send one request with a list of
            # all consumer groups. Java still hasn't implemented this
            # because the error checking is hard to get right when some
            # groups error and others don't.
            request = DescribeGroupsRequest[version](groups=(group_id,))
        else:
            request = DescribeGroupsRequest[version](
                groups=(group_id,),
                include_authorized_operations=True
            )
        return request

    def _describe_consumer_groups_process_response(self, response):
        """Process a DescribeGroupsResponse into a group description."""
        if response.API_VERSION > 3:
            raise NotImplementedError(
                "Support for DescribeGroupsResponse_v{} has not yet been added to KafkaAdminClient."
                .format(response.API_VERSION))

        assert len(response.groups) == 1
        for response_field, response_name in zip(response.SCHEMA.fields, response.SCHEMA.names):
            if isinstance(response_field, Array):
                described_groups_field_schema = response_field.array_of
                described_group = getattr(response, response_name)[0]
                described_group_information_list = []
                protocol_type_is_consumer = False
                for (described_group_information, group_information_name, group_information_field) in zip(described_group, described_groups_field_schema.names, described_groups_field_schema.fields):
                    if group_information_name == 'protocol_type':
                        protocol_type = described_group_information
                        protocol_type_is_consumer = (protocol_type == ConsumerProtocol_v0.PROTOCOL_TYPE or not protocol_type)
                    if isinstance(group_information_field, Array):
                        member_information_list = []
                        member_schema = group_information_field.array_of
                        for members in described_group_information:
                            member_information = []
                            for (member, member_field, member_name)  in zip(members, member_schema.fields, member_schema.names):
                                if protocol_type_is_consumer:
                                    if member_name == 'member_metadata' and member:
                                        member_information.append(ConsumerProtocolMemberMetadata_v0.decode(member))
                                    elif member_name == 'member_assignment' and member:
                                        member_information.append(ConsumerProtocolMemberAssignment_v0.decode(member))
                                    else:
                                        member_information.append(member)
                            member_info_tuple = MemberInformation._make(member_information)
                            member_information_list.append(member_info_tuple)
                        described_group_information_list.append(member_information_list)
                    else:
                        described_group_information_list.append(described_group_information)
                # Version 3 of the DescribeGroups API introduced the "authorized_operations" field.
                if response.API_VERSION >= 3:
                    described_group_information_list[-1] = list(map(lambda acl: acl.name, valid_acl_operations(described_group_information_list[-1])))
                else:
                    # TODO: Fix GroupInformation defaults
                    described_group_information_list.append([])
                group_description = GroupInformation._make(described_group_information_list)
        error_code = group_description.error_code
        error_type = Errors.for_code(error_code)
        # Java has the note: KAFKA-6789, we can retry based on the error code
        if error_type is not Errors.NoError:
            raise error_type(
                "DescribeGroupsResponse failed with response '{}'."
                .format(response))
        return group_description

    def describe_consumer_groups(self, group_ids, group_coordinator_id=None, include_authorized_operations=False):
        """Describe a set of consumer groups.

        Any errors are immediately raised.

        Arguments:
            group_ids: A list of consumer group IDs. These are typically the
                group names as strings.

        Keyword Arguments:
            group_coordinator_id (int, optional): The node_id of the groups' coordinator
                broker. If set to None, it will query the cluster for each group to
                find that group's coordinator. Explicitly specifying this can be
                useful for avoiding extra network round trips if you already know
                the group coordinator. This is only useful when all the group_ids
                have the same coordinator, otherwise it will error. Default: None.

        Returns:
            A list of group descriptions. For now the group descriptions
            are the raw results from the DescribeGroupsResponse. Long-term, we
            plan to change this to return namedtuples as well as decoding the
            partition assignments.
        """
        if group_coordinator_id is not None:
            groups_coordinators = {group_id: group_coordinator_id for group_id in group_ids}
        else:
            groups_coordinators = self._find_coordinator_ids(group_ids)

        requests = [
            (self._describe_consumer_groups_request(group_id), coordinator_id)
            for group_id, coordinator_id in groups_coordinators.items()
        ]
        return self.send_requests(requests, response_fn=self._describe_consumer_groups_process_response)

    def _list_consumer_groups_request(self):
        """Send a ListGroupsRequest to a broker.

        Returns:
            ListGroupsRequest object
        """
        version = self._client.api_version(ListGroupsRequest, max_version=2)
        return ListGroupsRequest[version]()

    def _list_consumer_groups_process_response(self, response):
        """Process a ListGroupsResponse into a list of groups."""
        if response.API_VERSION <= 2:
            error_type = Errors.for_code(response.error_code)
            if error_type is not Errors.NoError:
                raise error_type(
                    "ListGroupsRequest failed with response '{}'."
                    .format(response))
        else:
            raise NotImplementedError(
                "Support for ListGroupsResponse_v{} has not yet been added to KafkaAdminClient."
                .format(response.API_VERSION))
        return response.groups

    def list_consumer_groups(self, broker_ids=None):
        """List all consumer groups known to the cluster.

        This returns a list of Consumer Group tuples. The tuples are
        composed of the consumer group name and the consumer group protocol
        type.

        Only consumer groups that store their offsets in Kafka are returned.
        The protocol type will be an empty string for groups created using
        Kafka < 0.9 APIs because, although they store their offsets in Kafka,
        they don't use Kafka for group coordination. For groups created using
        Kafka >= 0.9, the protocol type will typically be "consumer".

        As soon as any error is encountered, it is immediately raised.

        Keyword Arguments:
            broker_ids ([int], optional): A list of broker node_ids to query for consumer
                groups. If set to None, will query all brokers in the cluster.
                Explicitly specifying broker(s) can be useful for determining which
                consumer groups are coordinated by those broker(s). Default: None

        Returns:
            list: List of tuples of Consumer Groups.

        Raises:
            CoordinatorNotAvailableError: The coordinator is not
                available, so cannot process requests.
            CoordinatorLoadInProgressError: The coordinator is loading and
                hence can't process requests.
        """
        # While we return a list, internally use a set to prevent duplicates
        # because if a group coordinator fails after being queried, and its
        # consumer groups move to new brokers that haven't yet been queried,
        # then the same group could be returned by multiple brokers.
        if broker_ids is None:
            broker_ids = [broker.nodeId for broker in self._client.cluster.brokers()]
        requests = [
            (self._list_consumer_groups_request(), broker_id)
            for broker_id in broker_ids
        ]
        consumer_groups = self.send_requests(requests, response_fn=self._list_consumer_groups_process_response)
        return list(set().union(*consumer_groups))

    def _list_consumer_group_offsets_request(self, group_id, partitions=None):
        """Send an OffsetFetchRequest to a broker.

        Arguments:
            group_id (str): The consumer group id name for which to fetch offsets.

        Keyword Arguments:
            partitions: A list of TopicPartitions for which to fetch
                offsets. On brokers >= 0.10.2, this can be set to None to fetch all
                known offsets for the consumer group. Default: None.

        Returns:
            OffsetFetchRequest object
        """
        version = self._client.api_version(OffsetFetchRequest, max_version=5)
        if partitions is None:
            if version <= 1:
                raise ValueError(
                    """OffsetFetchRequest_v{} requires specifying the
                    partitions for which to fetch offsets. Omitting the
                    partitions is only supported on brokers >= 0.10.2.
                    For details, see KIP-88.""".format(version))
            topics_partitions = None
        else:
            # transform from [TopicPartition("t1", 1), TopicPartition("t1", 2)] to [("t1", [1, 2])]
            topics_partitions_dict = defaultdict(set)
            for topic, partition in partitions:
                topics_partitions_dict[topic].add(partition)
            topics_partitions = list(six.iteritems(topics_partitions_dict))
        return OffsetFetchRequest[version](group_id, topics_partitions)

    def _list_consumer_group_offsets_process_response(self, response):
        """Process an OffsetFetchResponse.

        Arguments:
            response: an OffsetFetchResponse.

        Returns:
            A dictionary composed of TopicPartition keys and
            OffsetAndMetadata values.
        """
        if response.API_VERSION <= 5:

            # OffsetFetchResponse_v1 lacks a top-level error_code
            if response.API_VERSION > 1:
                error_type = Errors.for_code(response.error_code)
                if error_type is not Errors.NoError:
                    # optionally we could retry if error_type.retriable
                    raise error_type(
                        "OffsetFetchResponse failed with response '{}'."
                        .format(response))

            # transform response into a dictionary with TopicPartition keys and
            # OffsetAndMetadata values--this is what the Java AdminClient returns
            offsets = {}
            for topic, partitions in response.topics:
                for partition_data in partitions:
                    if response.API_VERSION <= 4:
                        partition, offset, metadata, error_code = partition_data
                        leader_epoch = -1
                    else:
                        partition, offset, leader_epoch, metadata, error_code = partition_data
                    error_type = Errors.for_code(error_code)
                    if error_type is not Errors.NoError:
                        raise error_type(
                            "Unable to fetch consumer group offsets for topic {}, partition {}"
                            .format(topic, partition))
                    offsets[TopicPartition(topic, partition)] = OffsetAndMetadata(offset, metadata, leader_epoch)
        else:
            raise NotImplementedError(
                "Support for OffsetFetchResponse_v{} has not yet been added to KafkaAdminClient."
                .format(response.API_VERSION))
        return offsets

    def list_consumer_group_offsets(self, group_id, group_coordinator_id=None,
                                    partitions=None):
        """Fetch Consumer Offsets for a single consumer group.

        Note:
        This does not verify that the group_id or partitions actually exist
        in the cluster.

        As soon as any error is encountered, it is immediately raised.

        Arguments:
            group_id (str): The consumer group id name for which to fetch offsets.

        Keyword Arguments:
            group_coordinator_id (int, optional): The node_id of the group's coordinator
                broker. If set to None, will query the cluster to find the group
                coordinator. Explicitly specifying this can be useful to prevent
                that extra network round trip if you already know the group
                coordinator. Default: None.
            partitions: A list of TopicPartitions for which to fetch
                offsets. On brokers >= 0.10.2, this can be set to None to fetch all
                known offsets for the consumer group. Default: None.

        Returns:
            dictionary: A dictionary with TopicPartition keys and
            OffsetAndMetadata values. Partitions that are not specified and for
            which the group_id does not have a recorded offset are omitted. An
            offset value of `-1` indicates the group_id has no offset for that
            TopicPartition. A `-1` can only happen for partitions that are
            explicitly specified.
        """
        if group_coordinator_id is None:
            group_coordinator_id = self._find_coordinator_ids([group_id])[group_id]
        request = self._list_consumer_group_offsets_request(group_id, partitions)
        response = self.send_request(request, node_id=group_coordinator_id)
        return self._list_consumer_group_offsets_process_response(response)

    def delete_consumer_groups(self, group_ids, group_coordinator_id=None):
        """Delete Consumer Group Offsets for given consumer groups.

        Note:
        This does not verify that the group ids actually exist and
        group_coordinator_id is the correct coordinator for all these groups.

        The result needs checking for potential errors.

        Arguments:
            group_ids ([str]): The consumer group ids of the groups which are to be deleted.

        Keyword Arguments:
            group_coordinator_id (int, optional): The node_id of the broker which is
                the coordinator for all the groups. Use only if all groups are coordinated
                by the same broker. If set to None, will query the cluster to find the coordinator
                for every single group. Explicitly specifying this can be useful to prevent
                that extra network round trips if you already know the group coordinator.
                Default: None.

        Returns:
            A list of tuples (group_id, KafkaError)
        """
        coordinators_groups = defaultdict(list)
        if group_coordinator_id is not None:
            coordinators_groups[group_coordinator_id] = group_ids
        else:
            for group_id, coordinator_id in self._find_coordinator_ids(group_ids).items():
                coordinators_groups[coordinator_id].append(group_id)

        requests = [
            (self._delete_consumer_groups_request(group_ids), coordinator_id)
            for coordinator_id, group_ids in coordinators_groups.items()
        ]

        results = self.send_requests(requests, response_fn=self._convert_delete_groups_response)
        return list(itertools.chain(*results))

    def _convert_delete_groups_response(self, response):
        """Parse the DeleteGroupsResponse, mapping group IDs to their respective errors.

        Arguments:
            response: A DeleteGroupsResponse object from the broker.

        Returns:
            A list of (group_id, KafkaError) for each deleted group.
        """
        if response.API_VERSION <= 1:
            results = []
            for group_id, error_code in response.results:
                results.append((group_id, Errors.for_code(error_code)))
            return results
        else:
            raise NotImplementedError(
                "Support for DeleteGroupsResponse_v{} has not yet been added to KafkaAdminClient."
                    .format(response.API_VERSION))

    def _delete_consumer_groups_request(self, group_ids):
        """Build a DeleteGroupsRequest to send to a broker (the group coordinator).

        Arguments:
            group_ids ([str]): A list of consumer group IDs to be deleted.

        Returns:
            A DeleteGroupsRequest object.
        """
        version = self._client.api_version(DeleteGroupsRequest, max_version=1)
        return DeleteGroupsRequest[version](group_ids)

    @staticmethod
    def _convert_topic_partitions(topic_partitions):
        return [
            (
                topic,
                partition_ids
            )
            for topic, partition_ids in topic_partitions.items()
        ]

    def _get_all_topic_partitions(self):
        return [
            (
                topic,
                [partition_info.partition for partition_info in self._client.cluster._partitions[topic].values()]
            )
            for topic in self._client.cluster.topics()
        ]

    def _get_topic_partitions(self, topic_partitions):
        if topic_partitions is None:
            return self._get_all_topic_partitions()
        return self._convert_topic_partitions(topic_partitions)

    def perform_leader_election(self, election_type, topic_partitions=None, timeout_ms=None):
        """Perform leader election on the topic partitions.

        :param election_type: Type of election to attempt. 0 for Perferred, 1 for Unclean
        :param topic_partitions: A map of topic name strings to partition ids list.
            By default, will run on all topic partitions
        :param timeout_ms: Milliseconds to wait for the leader election process to complete
            before the broker returns.

        :return: Appropriate version of ElectLeadersResponse class.
        """
        version = self._client.api_version(ElectLeadersRequest, max_version=1)
        timeout_ms = self._validate_timeout(timeout_ms)
        request = ElectLeadersRequest[version](
            election_type=ElectionType(election_type),
            topic_partitions=self._get_topic_partitions(topic_partitions),
            timeout=timeout_ms,
        )
        # TODO convert structs to a more pythonic interface
        return self._send_request_to_controller(request)

    def describe_log_dirs(self):
        """Send a DescribeLogDirsRequest request to a broker.

        Returns:
            DescribeLogDirsResponse object
        """
        version = self._client.api_version(DescribeLogDirsRequest, max_version=0)
        return self.send_request(DescribeLogDirsRequest[version]())
