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
from flask_mqtt import Mqtt, MQTT_ERR_SUCCESS


def wait(seconds=2):
    time.sleep(seconds)


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
        self.subscribe_handled = False
        self.unsubscribe_handled = False

        @self.mqtt.on_subscribe()
        def handle_subscribe(client, userdata, mid_, granted_qos):
            self.subscribe_handled = True

        @self.mqtt.on_unsubscribe()
        def handle_unsubscribe(client, userdata, mid_):
            self.unsubscribe_handled = True

        ret, mid = self.mqtt.subscribe('home/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()

        ret, mid = self.mqtt.unsubscribe('home/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()

        self.assertTrue(self.subscribe_handled)
        self.assertTrue(self.unsubscribe_handled)

    def test_qos(self):
        self.mqtt = Mqtt(self.app)

        # subscribe to a topic with qos = 1
        self.mqtt.subscribe('test', 1)
        self.assertEqual(1, len(self.mqtt.topics))
        self.assertEqual(('test', 1), self.mqtt.topics['test'])

        # subscribe to same topic, overwrite qos
        self.mqtt.subscribe('test', 2)
        self.assertEqual(1, len(self.mqtt.topics))
        self.assertEqual(('test', 2), self.mqtt.topics['test'])

        # unsubscribe
        self.mqtt.unsubscribe('test')
        self.assertEqual(0, len(self.mqtt.topics))

    def test_topic_count(self):
        self.mqtt = Mqtt(self.app)

        ret, mid = self.mqtt.subscribe('test')
        self.assertEqual(1, len(self.mqtt.topics))

        ret, mid = self.mqtt.subscribe('test')
        self.assertEqual(1, len(self.mqtt.topics))

        self.mqtt.unsubscribe('test')
        self.assertEqual(0, len(self.mqtt.topics))

        self.mqtt.unsubscribe('test')
        self.assertEqual(0, len(self.mqtt.topics))

        ret, mid = self.mqtt.subscribe('test1')
        ret, mid = self.mqtt.subscribe('test2')
        self.assertEqual(2, len(self.mqtt.topics))
        self.mqtt.unsubscribe_all()
        self.assertEqual(0, len(self.mqtt.topics))
        self.mqtt._disconnect()

    def test_publish(self):

        self.mqtt = Mqtt(self.app)
        self.handled_message = False
        self.handled_topic = False
        self.handled_publish = False

        @self.mqtt.on_message()
        def handle_message(client, userdata, message):
            self.handled_message = True

        @self.mqtt.on_publish()
        def handle_publish(client, userdata, mid):
            self.handled_publish = True

        self.mqtt.subscribe('home/test')
        wait()
        self.mqtt.publish('home/test', 'hello world')
        wait()

        self.assertTrue(self.handled_message)
        # self.assertTrue(self.handled_topic)
        self.assertTrue(self.handled_publish)

    def test_on_topic(self):

        self.mqtt = Mqtt(self.app)
        self.handled_message = False
        self.handled_topic = False

        @self.mqtt.on_message()
        def handle_message(client, userdata, message):
            self.handled_message = True

        @self.mqtt.on_topic('home/test')
        def handle_on_topic(*args, **kwargs):
            self.handled_topic = True

        @self.mqtt.on_connect()
        def handle_connect(*args, **kwargs):
            self.mqtt.subscribe('home/test')

        wait()
        self.mqtt.publish('home/test', 'hello world')
        wait()

        self.assertFalse(self.handled_message)
        self.assertTrue(self.handled_topic)

    def test_logging(self):
        self.mqtt = Mqtt(self.app)

        @self.mqtt.on_log()
        def handle_logging(client, userdata, level, buf):
            self.assertIsNotNone(client)
            self.assertIsNotNone(level)
            self.assertIsNotNone(buf)

        self.mqtt.publish('test', 'hello world')

    def test_disconnect(self):
        self.mqtt = Mqtt()
        self.connected = False

        @self.mqtt.on_connect()
        def handle_connect(*args, **kwargs):
            self.connected = True

        @self.mqtt.on_disconnect()
        def handle_disconnect(*args, **kwargs):
            self.connected = False

        self.assertFalse(self.connected)
        self.mqtt.init_app(self.app)
        wait()
        self.assertTrue(self.connected)
        self.mqtt._disconnect()
        wait()
        self.assertFalse(self.connected)


if __name__ == '__main__':
    unittest.main()
