import time
import ssl
from flask import Flask
from typing import Tuple, List, Callable, Any, Dict
from paho.mqtt.client import Client, MQTT_ERR_SUCCESS, MQTT_ERR_ACL_DENIED, \
    MQTT_ERR_AGAIN, MQTT_ERR_AUTH, MQTT_ERR_CONN_LOST, MQTT_ERR_CONN_REFUSED, \
    MQTT_ERR_ERRNO, MQTT_ERR_INVAL, MQTT_ERR_NO_CONN, MQTT_ERR_NOMEM, \
    MQTT_ERR_NOT_FOUND, MQTT_ERR_NOT_SUPPORTED, MQTT_ERR_PAYLOAD_SIZE, \
    MQTT_ERR_PROTOCOL, MQTT_ERR_QUEUE_SIZE, MQTT_ERR_TLS, MQTT_ERR_UNKNOWN, \
    MQTT_LOG_DEBUG, MQTT_LOG_ERR, MQTT_LOG_INFO, MQTT_LOG_NOTICE, \
    MQTT_LOG_WARNING


__version__ = '0.0.5'


class Mqtt():

    def __init__(self, app: Flask=None) -> None:
        self.app = app
        self.client = Client()
        self.client.on_connect = self._handle_connect
        self.client.on_disconnect = self._handle_disconnect
        self.topics = []  #: type: List
        self.connected = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.username = app.config.get('MQTT_USERNAME')
        self.password = app.config.get('MQTT_PASSWORD')
        self.broker_url = app.config.get('MQTT_BROKER_URL', 'localhost')
        self.broker_port = app.config.get('MQTT_BROKER_PORT', 1883)
        self.tls_enabled = app.config.get('MQTT_TLS_ENABLED', False)
        self.keepalive = app.config.get('MQTT_KEEPALIVE', 60)

        if self.tls_enabled:
            self.tls_ca_certs = app.config['MQTT_TLS_CA_CERTS']
            self.tls_certfile = app.config.get('MQTT_TLS_CERTFILE')
            self.tls_keyfile = app.config.get('MQTT_TLS_KEYFILE')
            self.tls_cert_reqs = app.config.get('MQTT_TLS_CERT_REQS', ssl.CERT_REQUIRED)
            self.tls_version = app.config.get('MQTT_TLS_VERSION', ssl.PROTOCOL_TLSv1)
            self.tls_ciphers = app.config.get('MQTT_TLS_CIPHERS')
            self.tls_insecure = app.config.get('MQTT_TLS_INSECURE', False)

        self._connect()

    def _connect(self) -> None:

        if self.username is not None:
            self.client.username_pw_set(self.username, self.password)

        # security
        if self.tls_enabled:
            if self.tls_insecure:
                self.client.tls_insecure_set(self.tls_insecure)

            self.client.tls_set(
                ca_certs=self.tls_ca_certs,
                certfile=self.tls_certfile,
                keyfile=self.tls_keyfile,
                cert_reqs=self.tls_cert_reqs,
                tls_version=self.tls_version,
                ciphers=self.tls_ciphers,
            )

        self.client.loop_start()
        res = self.client.connect(
                self.broker_url, self.broker_port,
                keepalive=self.keepalive
        )

    def _disconnect(self) -> None:
        self.client.disconnect()

    def _handle_connect(self, client: Client, userdata: Any, flags: Dict, 
                        rc: int) -> None:
        if rc == MQTT_ERR_SUCCESS:
            self.connected = True
            for topic in self.topics:
                self.client.subscribe(topic)

    def _handle_disconnect(self, client: str, userdata: Any, rc: int) -> None:
        self.connected = False

    def on_topic(self, topic: str) -> Callable:
        """
        Decorator to add a callback function that is called when a certain
        topic has been published. The callback function is expected to have the
        following form: `handle_topic(client, userdata, message)`

        :parameter topic: a string specifying the subscription topic to subscribe to

        **Example usage:**

        ::

            @on_topic('home/mytopic')
            def handle_mytopic(client, userdata, message):
                print('Received message on topic {}: {}'
                      .format(message.topic, message.payload.decode()))

        """
        def decorator(handler: Callable[[str], None]) -> Callable[[str], None]:
            self.client.message_callback_add(topic, handler)
            return handler
        return decorator

    def subscribe(self, topic: str, qos: int=0) -> None:
        """
        Subscribe to a certain topic.

        :param topic: a string specifying the subscription topic to subscribe to.
        :param qos: the desired quality of service level for the subscription.
                    Defaults to 0.

        A topic is a UTF-8 string, which is used by the broker to filter
        messages for each connected client. A topic consists of one or more
        topic levels. Each topic level is separated by a forward slash
        (topic level separator).

        **Topic example:** `myhome/groundfloor/livingroom/temperature`

        """
        # TODO: add support for list of topics
        # don't subscribe if already subscribed
        if topic in self.topics:
            return

        # try to subscribe
        result, mid = self.client.subscribe(topic, qos)

        # if successful add to topics
        if result == MQTT_ERR_SUCCESS:
            self.topics.append(topic)

        return result

    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from a single topic.

        :param topic: a single string that is the subscription topic to
                      unsubscribe from

        """
        # don't unsubscribe if not in topics
        if topic not in self.topics:
            return

        result, mid = self.client.unsubscribe(topic)

        # if successful remove from topics
        if result == MQTT_ERR_SUCCESS:
            self.topics.remove(topic)

        return result

    def unsubscribe_all(self) -> None:
        """
        Unsubscribe from all topics.

        """
        topics = self.topics[:]
        for topic in topics:
            self.unsubscribe(topic)

    def publish(self, topic: str, payload: bytes=None, qos: int=0,
                retain: bool=False) -> Tuple[int, int]:
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
        return self.client.publish(topic, payload, qos, retain)

    def on_message(self) -> Callable:
        """
        Decorator to handle all messages that have been subscribed.

        **Example Usage:**

        ::

            @mqtt.on_message()
            def handle_messages(client, userdata, message):
                print('Received message on topic {}: {}'
                      .format(message.topic, message.payload.decode()))

        """
        def decorator(handler: Callable) -> Callable:
            self.client.on_message = handler
            return handler
        return decorator

    def on_log(self) -> Callable:
        """
        Decorator to handle MQTT logging.

        **Example Usage:**

        ::
            
            @mqtt.on_log()
            def handle_logging(client, userdata, level, buf):
                print(client, userdata, level, buf)

        """
        def decorator(handler: Callable) -> Callable:
            self.client.on_log = handler
            return handler
        return decorator

