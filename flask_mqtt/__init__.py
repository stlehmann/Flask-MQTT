import time
from threading import Thread
from paho.mqtt.client import Client, MQTTMessage


__version__ = '0.0.1'


class Mqtt():

    def __init__(self, app=None):
        self.app = app
        self.client = Client()
        self.mqtt_thread = Thread(target=self.loop_forever)
        self.mqtt_thread.daemon = True

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.connect()

    def connect(self):
        self.client.username_pw_set(self.app.config['MQTT_USERNAME'], self.app.config['MQTT_PASSWORD'])
        res = self.client.connect(self.app.config['MQTT_BROKER_URL'], self.app.config['MQTT_BROKER_PORT'])
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
        return self.client.subscribe(topic, qos)

    def publish(self, topic, payload=None, qos=0, retain=False):
        return self.client.publish(topic, payload, qos, retain)

    def on_message(self):
        def decorator(handler):
            self.client.on_message = handler
            return handler
        return decorator

