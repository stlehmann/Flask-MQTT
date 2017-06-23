import sys
import unittest
import time
from flask import Flask

# remove mocks and import flask_mqtt
try:
    sys.modules.pop('paho.mqtt.client')
    sys.modules.pop('flask_mqtt')
except KeyError:
    pass
from flask_mqtt import Mqtt


class FlaskMQTTTestCase(unittest.TestCase):

    def setUp(self):

        self.app = Flask(__name__)

    def test_simple_connect(self):
        self.mqtt = Mqtt(self.app)
        self.mqtt._disconnect()

    def test_connect_with_username(self):
        self.app.config['MQTT_USERNAME'] = 'user'
        self.app.config['MQTT_PASSWORD'] = 'secret'
        self.mqtt = Mqtt(self.app)
        self.mqtt._disconnect()

    def test_subscribe(self):
        self.mqtt = Mqtt(self.app)
        self.mqtt.subscribe('test')
        self.assertEqual('test', self.mqtt.topics[0])
        self.assertEqual(1, len(self.mqtt.topics))
        self.mqtt.subscribe('test')
        self.assertEqual(1, len(self.mqtt.topics))
        self.mqtt.unsubscribe('test')
        self.assertEqual(0, len(self.mqtt.topics))
        self.mqtt.unsubscribe('test')

        self.mqtt.subscribe('test1')
        self.mqtt.subscribe('test2')
        self.assertEqual(2, len(self.mqtt.topics))
        self.mqtt.unsubscribe_all()
        self.assertEqual(0, len(self.mqtt.topics))
        self.mqtt._disconnect()

    def test_publish(self):

        self.mqtt = Mqtt(self.app)

        @self.mqtt.on_message()
        def handle_message(client, userdata, message):
            print(message)

        @self.mqtt.on_topic('test')
        def handle_on_topic(*args, **kwargs):
            pass

        self.mqtt.subscribe('test')
        self.mqtt.publish('test', 'hello world')
        time.sleep(2)

    def test_logging(self):
        self.mqtt = Mqtt(self.app)

        @self.mqtt.on_log()
        def handle_logging(client, userdata, level, buf):
            self.assertIsNotNone(client)
            self.assertIsNotNone(level)
            self.assertIsNotNone(buf)

        self.mqtt.publish('test', 'hello world')


