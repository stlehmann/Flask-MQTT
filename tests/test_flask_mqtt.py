import unittest
from flask import Flask
from flask_mqtt import Mqtt


class FlaskMQTTTestCase(unittest.TestCase):

    def setUp(self):

        self.app = Flask(__name__)

    def test_simple_connect(self):
        self.mqtt = Mqtt(self.app)
        self.mqtt.disconnect()

    def test_connect_with_username(self):
        self.app.config['MQTT_USERNAME'] = 'user'
        self.app.config['MQTT_PASSWORD'] = 'secret'
        self.mqtt = Mqtt(self.app)
        self.mqtt.disconnect()

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
        self.mqtt.disconnect()
