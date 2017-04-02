import time
from threading import Thread
from paho.mqtt.client import Client, MQTT_ERR_SUCCESS


__version__ = '0.0.1'


class Mqtt():

    def __init__(self, app=None):
        self.app = app
        self.client = Client()
        self.topics = []
        self.mqtt_thread = Thread(target=self.loop_forever)
        self.mqtt_thread.daemon = True

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.connect()

    def connect(self):
        self.client.username_pw_set(self.app.config['MQTT_USERNAME'],
                                    self.app.config['MQTT_PASSWORD'])
        res = self.client.connect(self.app.config['MQTT_BROKER_URL'],
                                  self.app.config['MQTT_BROKER_PORT'])
        if res == 0:
            self.mqtt_thread.start()

    def disconnect(self):
        self.client.disconnect()

    def loop_forever(self):
        while True:
            time.sleep(self.app.config['MQTT_REFRESH_TIME'])
            self.client.loop(timeout=1.0, max_packets=1)

    def on_topic(self, topic):
        def decorator(handler):
            self.client.message_callback_add(topic, handler)
            return handler
        return decorator

    def subscribe(self, topic, qos=0):
        """
        :todo: add support for list of topics

        """
        # don't subscribe if already subscribed
        if topic in self.topics:
            return

        # try to subscribe
        result, mid = self.client.subscribe(topic, qos)

        # if successful add to topics
        if result == MQTT_ERR_SUCCESS:
            self.topics.append(topic)

        return result

    def unsubscribe(self, topic):
        # don't unsubscribe if not in topics
        if topic not in self.topics:
            return

        result, mid = self.client.unsubscribe(topic)

        # if successful remove from topics
        if result == MQTT_ERR_SUCCESS:
            self.topics.remove(topic)

        return result

    def unsubscribe_all(self):
        topics = self.topics[:]
        for topic in topics:
            self.unsubscribe(topic)

    def publish(self, topic, payload=None, qos=0, retain=False):
        return self.client.publish(topic, payload, qos, retain)

    def on_message(self):
        def decorator(handler):
            self.client.on_message = handler
            return handler
        return decorator
