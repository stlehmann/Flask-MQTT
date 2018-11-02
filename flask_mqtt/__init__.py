"""Flask-MQTT Package.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-04-19 19:43:41
:last modified by:   Stefan Lehmann
:last modified time: 2018-11-02 18:07:39

"""
import sys
import ssl
import logging
try:
    from flask.logging import default_handler
except ImportError:  # For flask versions before 1.0
    default_handler = logging.StreamHandler()
    default_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
from collections import namedtuple
from flask import Flask  # noqa: F401
from typing import Dict, Any, Callable, Tuple, Optional  # noqa: F401
from paho.mqtt.client import (  # noqa: F401
    Client,
    MQTT_ERR_SUCCESS,
    MQTT_ERR_ACL_DENIED,
    MQTT_ERR_AGAIN,
    MQTT_ERR_AUTH,
    MQTT_ERR_CONN_LOST,
    MQTT_ERR_CONN_REFUSED,
    MQTT_ERR_ERRNO,
    MQTT_ERR_INVAL,
    MQTT_ERR_NO_CONN,
    MQTT_ERR_NOMEM,
    MQTT_ERR_NOT_FOUND,
    MQTT_ERR_NOT_SUPPORTED,
    MQTT_ERR_PAYLOAD_SIZE,
    MQTT_ERR_PROTOCOL,
    MQTT_ERR_QUEUE_SIZE,
    MQTT_ERR_TLS,
    MQTT_ERR_UNKNOWN,
    MQTT_LOG_DEBUG,
    MQTT_LOG_ERR,
    MQTT_LOG_INFO,
    MQTT_LOG_NOTICE,
    MQTT_LOG_WARNING,
    MQTTv311,
    MQTTv31,
)


# define some alias for python2 compatibility
if sys.version_info[0] >= 3:
    unicode = str


# current Flask-MQTT version
__version__ = "1.0.5"


#: Container for topic + qos
TopicQos = namedtuple("TopicQos", ["topic", "qos"])


# Init logger
logger = logging.getLogger('flask.flask_mqtt')
logger.setLevel(logging.DEBUG)
logger.addHandler(default_handler)


class Mqtt():
    """Main Mqtt class."""

    def __init__(self, app=None):
        # type: (Flask) -> None
        self.app = app
        self._connect_handler = None  # type: Optional[Callable]
        self._disconnect_handler = None  # type: Optional[Callable]
        self.topics = {}  # type: Dict[str, TopicQos]
        self.connected = False
        self.client = Client()

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # type: (Flask) -> None
        """Init the Flask-MQTT addon."""
        self.client_id = app.config.get("MQTT_CLIENT_ID", "")
        if isinstance(self.client_id, unicode):
            self.client._client_id = self.client_id.encode('utf-8')
        else:
            self.client._client_id = self.client_id
        self.client._transport = app.config.get("MQTT_TRANSPORT", "tcp").lower()
        self.client._protocol = app.config.get("MQTT_PROTOCOL_VERSION", MQTTv311)

        self.client.on_connect = self._handle_connect
        self.client.on_disconnect = self._handle_disconnect
        self.username = app.config.get("MQTT_USERNAME")
        self.password = app.config.get("MQTT_PASSWORD")
        self.broker_url = app.config.get("MQTT_BROKER_URL", "localhost")
        self.broker_port = app.config.get("MQTT_BROKER_PORT", 1883)
        self.tls_enabled = app.config.get("MQTT_TLS_ENABLED", False)
        self.keepalive = app.config.get("MQTT_KEEPALIVE", 60)
        self.last_will_topic = app.config.get("MQTT_LAST_WILL_TOPIC")
        self.last_will_message = app.config.get("MQTT_LAST_WILL_MESSAGE")
        self.last_will_qos = app.config.get("MQTT_LAST_WILL_QOS", 0)
        self.last_will_retain = app.config.get("MQTT_LAST_WILL_RETAIN", False)

        if self.tls_enabled:
            self.tls_ca_certs = app.config["MQTT_TLS_CA_CERTS"]
            self.tls_certfile = app.config.get("MQTT_TLS_CERTFILE")
            self.tls_keyfile = app.config.get("MQTT_TLS_KEYFILE")
            self.tls_cert_reqs = app.config.get("MQTT_TLS_CERT_REQS",
                                                ssl.CERT_REQUIRED)
            self.tls_version = app.config.get("MQTT_TLS_VERSION",
                                              ssl.PROTOCOL_TLSv1)
            self.tls_ciphers = app.config.get("MQTT_TLS_CIPHERS")
            self.tls_insecure = app.config.get("MQTT_TLS_INSECURE", False)

        # set last will message
        if self.last_will_topic is not None:
            self.client.will_set(
                self.last_will_topic,
                self.last_will_message,
                self.last_will_qos,
                self.last_will_retain,
            )

        self._connect()

    def _connect(self):
        # type: () -> None

        if self.username is not None:
            self.client.username_pw_set(self.username, self.password)

        # security
        if self.tls_enabled:
            self.client.tls_set(
                ca_certs=self.tls_ca_certs,
                certfile=self.tls_certfile,
                keyfile=self.tls_keyfile,
                cert_reqs=self.tls_cert_reqs,
                tls_version=self.tls_version,
                ciphers=self.tls_ciphers,
            )

            if self.tls_insecure:
                self.client.tls_insecure_set(self.tls_insecure)
        self.client.loop_start()

        res = self.client.connect(
            self.broker_url, self.broker_port, keepalive=self.keepalive
        )
        if res == 0:
            logger.debug(
                "Connected client '{0}' to broker {1}:{2}"
                .format(self.client_id, self.broker_url, self.broker_port)
            )
        else:
            logger.error(
                "Could not connect to MQTT Broker, Error Code: {0}".format(res)
            )

    def _disconnect(self):
        # type: () -> None
        self.client.loop_stop()
        self.client.disconnect()
        logger.debug('Disconnected from Broker')

    def _handle_connect(self, client, userdata, flags, rc):
        # type: (Client, Any, Dict, int) -> None
        if rc == MQTT_ERR_SUCCESS:
            self.connected = True
            for key, item in self.topics.items():
                self.client.subscribe(topic=item.topic, qos=item.qos)
        if self._connect_handler is not None:
            self._connect_handler(client, userdata, flags, rc)

    def _handle_disconnect(self, client, userdata, rc):
        # type: (str, Any, int) -> None
        self.connected = False
        if self._disconnect_handler is not None:
            self._disconnect_handler()

    def on_topic(self, topic):
        # type: (str) -> Callable
        """Decorator.

        Decorator to add a callback function that is called when a certain
        topic has been published. The callback function is expected to have the
        following form: `handle_topic(client, userdata, message)`

        :parameter topic: a string specifying the subscription topic to
            subscribe to

        The topic still needs to be subscribed via mqtt.subscribe() before the
        callback function can be used to handle a certain topic. This way it is
        possible to subscribe and unsubscribe during runtime.

        **Example usage:**::

            app = Flask(__name__)
            mqtt = Mqtt(app)
            mqtt.subscribe('home/mytopic')

            @mqtt.on_topic('home/mytopic')
            def handle_mytopic(client, userdata, message):
                print('Received message on topic {}: {}'
                      .format(message.topic, message.payload.decode()))
        """
        def decorator(handler):
            # type: (Callable[[str], None]) -> Callable[[str], None]
            self.client.message_callback_add(topic, handler)
            return handler

        return decorator

    def subscribe(self, topic, qos=0):
        # type: (str, int) -> Tuple[int, int]
        """
        Subscribe to a certain topic.

        :param topic: a string specifying the subscription topic to
            subscribe to.
        :param qos: the desired quality of service level for the subscription.
                    Defaults to 0.

        :rtype: (int, int)
        :result: (result, mid)

        A topic is a UTF-8 string, which is used by the broker to filter
        messages for each connected client. A topic consists of one or more
        topic levels. Each topic level is separated by a forward slash
        (topic level separator).

        The function returns a tuple (result, mid), where result is
        MQTT_ERR_SUCCESS to indicate success or (MQTT_ERR_NO_CONN, None) if the
        client is not currently connected.  mid is the message ID for the
        subscribe request. The mid value can be used to track the subscribe
        request by checking against the mid argument in the on_subscribe()
        callback if it is defined.

        **Topic example:** `myhome/groundfloor/livingroom/temperature`

        """
        # TODO: add support for list of topics

        # don't subscribe if already subscribed
        # try to subscribe
        result, mid = self.client.subscribe(topic=topic, qos=qos)

        # if successful add to topics
        if result == MQTT_ERR_SUCCESS:
            self.topics[topic] = TopicQos(topic=topic, qos=qos)
            logger.debug('Subscribed to topic: {0}, qos: {1}'
                         .format(topic, qos))
        else:
            logger.error('Error {0} subscribing to topic: {1}'
                         .format(result, topic))

        return (result, mid)

    def unsubscribe(self, topic):
        # type: (str) -> Optional[Tuple[int, int]]
        """
        Unsubscribe from a single topic.

        :param topic: a single string that is the subscription topic to
                      unsubscribe from

        :rtype: (int, int)
        :result: (result, mid)

        Returns a tuple (result, mid), where result is MQTT_ERR_SUCCESS
        to indicate success or (MQTT_ERR_NO_CONN, None) if the client is not
        currently connected.
        mid is the message ID for the unsubscribe request. The mid value can be
        used to track the unsubscribe request by checking against the mid
        argument in the on_unsubscribe() callback if it is defined.

        """
        # don't unsubscribe if not in topics
        if topic in self.topics:
            result, mid = self.client.unsubscribe(topic)

            if result == MQTT_ERR_SUCCESS:
                self.topics.pop(topic)
                logger.debug('Unsubscribed from topic: {0}'.format(topic))
            else:
                logger.debug('Error {0} unsubscribing from topic: {1}'
                             .format(result, topic))

            # if successful remove from topics
            return result, mid
        return None

    def unsubscribe_all(self):
        # type: () -> None
        """Unsubscribe from all topics."""
        topics = list(self.topics.keys())
        for topic in topics:
            self.unsubscribe(topic)

    def publish(self, topic, payload=None, qos=0, retain=False):
        # type: (str, bytes, int, bool) -> Tuple[int, int]
        """
        Send a message to the broker.

        :param topic: the topic that the message should be published on
        :param payload: the actual message to send. If not given, or set to
                        None a zero length message will be used. Passing an
                        int or float will result in the payload being
                        converted to a string representing that number.
                        If you wish to send a true int/float, use struct.pack()
                        to create the payload you require.
        :param qos: the quality of service level to use
        :param retain: if set to True, the message will be set as the
                       "last known good"/retained message for the topic

        :returns: Returns a tuple (result, mid), where result is
                  MQTT_ERR_SUCCESS to indicate success or MQTT_ERR_NO_CONN
                  if the client is not currently connected. mid is the message
                  ID for the publish request.

        """
        if not self.connected:
            self.client.reconnect()

        result, mid = self.client.publish(topic, payload, qos, retain)
        if result == MQTT_ERR_SUCCESS:
            logger.debug('Published topic {0}: {1}'.format(topic, payload))
        else:
            logger.error('Error {0} publishing topic {1}'
                         .format(result, topic))

        return (result, mid)

    def on_connect(self):
        # type: () -> Callable
        """Decorator.

        Decorator to handle the event when the broker responds to a connection
        request. Only the last decorated function will be called.

        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self._connect_handler = handler
            return handler

        return decorator

    def on_disconnect(self):
        # type: () -> Callable
        """Decorator.

        Decorator to handle the event when client disconnects from broker. Only
        the last decorated function will be called.

        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self._disconnect_handler = handler
            return handler

        return decorator

    def on_message(self):
        # type: () -> Callable
        """Decorator.

        Decorator to handle all messages that have been subscribed and that
        are not handled via the `on_message` decorator.

        **Note:** Unlike as written in the paho mqtt documentation this
        callback will not be called if there exists an topic-specific callback
        added by the `on_topic` decorator.

        **Example Usage:**::

            @mqtt.on_message()
            def handle_messages(client, userdata, message):
                print('Received message on topic {}: {}'
                      .format(message.topic, message.payload.decode()))
        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self.client.on_message = handler
            return handler

        return decorator

    def on_publish(self):
        # type: () -> Callable
        """Decorator.

        Decorator to handle all messages that have been published by the
        client.

        **Example Usage:**::

            @mqtt.on_publish()
            def handle_publish(client, userdata, mid):
                print('Published message with mid {}.'
                      .format(mid))
        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self.client.on_publish = handler
            return handler

        return decorator

    def on_subscribe(self):
        # type: () -> Callable
        """Decorate a callback function to handle subscritions.

        **Usage:**::

            @mqtt.on_subscribe()
            def handle_subscribe(client, userdata, mid, granted_qos):
                print('Subscription id {} granted with qos {}.'
                      .format(mid, granted_qos))
        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self.client.on_subscribe = handler
            return handler

        return decorator

    def on_unsubscribe(self):
        # type: () -> Callable
        """Decorate a callback funtion to handle unsubscribtions.

        **Usage:**::

            @mqtt.unsubscribe()
            def handle_unsubscribe(client, userdata, mid)
                print('Unsubscribed from topic (id: {})'
                      .format(mid)')
        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self.client.on_unsubscribe = handler
            return handler

        return decorator

    def on_log(self):
        # type: () -> Callable
        """Decorate a callback function to handle MQTT logging.

        **Example Usage:**

        ::

            @mqtt.on_log()
            def handle_logging(client, userdata, level, buf):
                print(client, userdata, level, buf)
        """
        def decorator(handler):
            # type: (Callable) -> Callable
            self.client.on_log = handler
            return handler

        return decorator
