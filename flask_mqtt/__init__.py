import time
import ssl
from typing import Tuple
from threading import Thread
from paho.mqtt.client import Client, MQTT_ERR_SUCCESS


__version__ = '0.0.2'


class Mqtt():

    def __init__(self, app=None):
        self.app = app
        self.client = Client()
        self.refresh_time = 1.0
        self.topics = []
        self.mqtt_thread = Thread(target=self._loop_forever)
        self.mqtt_thread.daemon = True

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.refresh_time = app.config.get('MQTT_REFRESH_TIME', 1.0)

        self.username = app.config.get('MQTT_USERNAME')
        self.password = app.config.get('MQTT_PASSWORD')
        self.broker_url = app.config.get('MQTT_BROKER_URL', 'localhost')
        self.broker_port = app.config.get('MQTT_BROKER_PORT', 1883)
        self.tls_enabled = app.config.get('MQTT_TLS_ENABLED', False)

        if self.tls_enabled:
            self.tls_ca_certs = app.config['MQTT_TLS_CA_CERTS']
            self.tls_certfile = app.config.get('MQTT_TLS_CERTFILE')
            self.tls_keyfile = app.config.get('MQTT_TLS_KEYFILE')
            self.tls_cert_reqs = app.config.get('MQTT_TLS_CERT_REQS', ssl.CERT_REQUIRED)
            self.tls_version = app.config.get('MQTT_TLS_VERSION', ssl.PROTOCOL_TLSv1)
            self.tls_ciphers = app.config.get('MQTT_TLS_CIPHERS')
            self.tls_insecure = app.config.get('MQTT_TLS_INSECURE', False)

        self._connect()

    def _connect(self):
        if not self.mqtt_thread.is_alive():

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

            res = self.client.connect(self.broker_url, self.broker_port)

            if res == 0:
                self.mqtt_thread.start()

    def _disconnect(self):
        self.client.disconnect()

    def _loop_forever(self):
        while True:
            time.sleep(self.refresh_time)
            self.client.loop(timeout=1.0, max_packets=1)

    def on_topic(self, topic: str):
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
        def decorator(handler):
            self.client.message_callback_add(topic, handler)
            return handler
        return decorator

    def subscribe(self, topic: str, qos: int=0):
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

    def unsubscribe(self, topic: str):
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

    def unsubscribe_all(self):
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
        return self.client.publish(topic, payload, qos, retain)

    def on_message(self):
        """
        Decorator to handle all messages that have been subscribed.

        **Example Usage:**

        ::

            @mqtt.on_message()
            def handle_messages(client, userdata, message):
                print('Received message on topic {}: {}'
                      .format(message.topic, message.payload.decode()))

        """
        def decorator(handler):
            self.client.on_message = handler
            return handler
        return decorator
