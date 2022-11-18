import sys
import unittest
import time
from flask import Flask

try:
    sys.modules.pop('paho.mqtt.client')
    sys.modules.pop('flask_mqtt')
except KeyError:
    pass
from flask_mqtt import Mqtt, MQTT_ERR_SUCCESS


def wait(seconds=0.5):
    time.sleep(seconds)


class FlaskMQTTTestCase(unittest.TestCase):
    def setUp(self):

        self.app = Flask(__name__)
        self.app.config['MQTT_USERNAME'] = 'mqtt'
        self.app.config['MQTT_PASSWORD'] = 'mqtt_server_one'
        
        self.app.config['MQTT2_USERNAME'] = 'mqtt2'
        self.app.config['MQTT2_PASSWORD'] = 'mqtt_server_two'
        self.app.config['MQTT2_BROKER_PORT'] = 1885
        
        self.app.config['MQTT3_USERNAME'] = 'mqtt3'
        self.app.config['MQTT3_PASSWORD'] = 'mqtt_server_three'
        self.app.config['MQTT3_BROKER_PORT'] = 1886

    def test_simple_connect(self):
        self.mqtt = Mqtt(self.app)
        self.mqtt._disconnect()

    def test_connect_same_config_prefix(self):
        self.mqtt = Mqtt(self.app)
        self.assertEqual(self.mqtt.username, 'mqtt')
        self.assertEqual(self.mqtt.password, 'mqtt_server_one')
        
        self.mqtt._disconnect()
    
    def test_connect_diff_config_prefix(self):
        self.mqtt = Mqtt(self.app, config_prefix="MQTT4")
        self.assertNotEqual(self.mqtt.username, 'mqtt')
        self.assertNotEqual(self.mqtt.password, 'mqtt_server_one')
        self.assertEqual(self.mqtt.username, None)
        self.assertEqual(self.mqtt.password, None)
        
        self.mqtt._disconnect()
    
    def test_connect_multiple_servers(self):
        self.mqtt = Mqtt(self.app, config_prefix="MQTT")
        self.mqtt2 = Mqtt(self.app, config_prefix="MQTT2")
        self.mqtt3 = Mqtt(self.app, config_prefix="MQTT3")
        
        self.assertEqual('mqtt', self.mqtt.username)
        self.assertEqual('mqtt2', self.mqtt2.username)
        self.assertEqual('mqtt3', self.mqtt3.username)
        self.assertEqual(1883, self.mqtt.broker_port)
        self.assertEqual(1885, self.mqtt2.broker_port)
        self.assertEqual(1886, self.mqtt3.broker_port)
        
        self.mqtt._disconnect()
        self.mqtt2._disconnect()
        self.mqtt3._disconnect()
    
    def test_subscribe_multiple_servers(self):
        self.subscribe_handled_mqtt = False
        self.unsubscribe_handled_mqtt = False
        self.subscribe_handled_mqtt2 = False
        self.unsubscribe_handled_mqtt2 = False
        self.subscribe_handled_mqtt3 = False
        self.unsubscribe_handled_mqtt3 = False
        
        self.mqtt = Mqtt(self.app, config_prefix="MQTT")
        self.mqtt2 = Mqtt(self.app, config_prefix="MQTT2")
        self.mqtt3 = Mqtt(self.app, config_prefix="MQTT3")
        
        @self.mqtt.on_subscribe()
        def handle_subscribe(client, userdata, mid_, granted_qos):
            self.subscribe_handled_mqtt = True
        
        @self.mqtt.on_unsubscribe()
        def handle_unsubscribe(client, userdata, mid_):
            self.unsubscribe_handled_mqtt = True
        
        @self.mqtt2.on_subscribe()
        def handle_subscribe(client, userdata, mid_, granted_qos):
            self.subscribe_handled_mqtt2 = True
        
        @self.mqtt2.on_unsubscribe()
        def handle_unsubscribe(client, userdata, mid_):
            self.unsubscribe_handled_mqtt2 = True
        
        @self.mqtt3.on_subscribe()
        def handle_subscribe(client, userdata, mid_, granted_qos):
            self.subscribe_handled_mqtt3 = True
        
        @self.mqtt3.on_unsubscribe()
        def handle_unsubscribe(client, userdata, mid_):
            self.unsubscribe_handled_mqtt3 = True

        ret, _ = self.mqtt.subscribe('mqtt/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()
        self.assertTrue(self.subscribe_handled_mqtt)
        ret, _ = self.mqtt.unsubscribe('mqtt/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()
        self.assertTrue(self.unsubscribe_handled_mqtt)
        
        ret, _ = self.mqtt2.subscribe('mqtt2/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()
        self.assertTrue(self.subscribe_handled_mqtt2)
        ret, _ = self.mqtt2.unsubscribe('mqtt2/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()
        self.assertTrue(self.unsubscribe_handled_mqtt2)
        
        
        ret, _ = self.mqtt3.subscribe('mqtt3/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()
        self.assertTrue(self.subscribe_handled_mqtt3)
        ret, _ = self.mqtt3.unsubscribe('mqtt3/test')
        self.assertEqual(ret, MQTT_ERR_SUCCESS)
        wait()
        self.assertTrue(self.unsubscribe_handled_mqtt3)

        
        self.mqtt._disconnect()
        self.mqtt2._disconnect()
        self.mqtt3._disconnect()
        
    def test_qos_multiple_servers(self):
        self.mqtt = Mqtt(self.app, config_prefix="MQTT")
        self.mqtt2 = Mqtt(self.app, config_prefix="MQTT2")
        self.mqtt3 = Mqtt(self.app, config_prefix="MQTT3")

        #### mqtt server one ####
        # subscribe to a topic with qos = 1
        self.mqtt.subscribe('mqtt/test', 1)
        self.assertEqual(1, len(self.mqtt.topics))
        self.assertEqual(('mqtt/test', 1), self.mqtt.topics['mqtt/test'])

        # subscribe to same topic, overwrite qos
        self.mqtt.subscribe('mqtt/test', 2)
        self.assertEqual(1, len(self.mqtt.topics))
        self.assertEqual(('mqtt/test', 2), self.mqtt.topics['mqtt/test'])

        # unsubscribe
        self.mqtt.unsubscribe('mqtt/test')
        self.assertEqual(0, len(self.mqtt.topics))
        
        #### mqtt server two ####
        # subscribe to a topic with qos = 1
        self.mqtt2.subscribe('mqtt2/test', 1)
        self.assertEqual(1, len(self.mqtt2.topics))
        self.assertEqual(('mqtt2/test', 1), self.mqtt2.topics['mqtt2/test'])

        # subscribe to same topic, overwrite qos
        self.mqtt2.subscribe('mqtt2/test', 2)
        self.assertEqual(1, len(self.mqtt2.topics))
        self.assertEqual(('mqtt2/test', 2), self.mqtt2.topics['mqtt2/test'])

        # unsubscribe
        self.mqtt2.unsubscribe('mqtt2/test')
        self.assertEqual(0, len(self.mqtt2.topics))
        
        #### mqtt server three ####
        # subscribe to a topic with qos = 1
        self.mqtt3.subscribe('mqtt3/test', 1)
        self.assertEqual(1, len(self.mqtt3.topics))
        self.assertEqual(('mqtt3/test', 1), self.mqtt3.topics['mqtt3/test'])

        # subscribe to same topic, overwrite qos
        self.mqtt3.subscribe('mqtt3/test', 2)
        self.assertEqual(1, len(self.mqtt3.topics))
        self.assertEqual(('mqtt3/test', 2), self.mqtt3.topics['mqtt3/test'])

        # unsubscribe
        self.mqtt3.unsubscribe('mqtt3/test')
        self.assertEqual(0, len(self.mqtt3.topics))
        
        self.mqtt._disconnect()
        self.mqtt2._disconnect()
        self.mqtt3._disconnect()
    
    def test_topic_count_multiple_servers(self):
        self.mqtt = Mqtt(self.app, config_prefix="MQTT")
        self.mqtt2 = Mqtt(self.app, config_prefix="MQTT2")
        self.mqtt3 = Mqtt(self.app, config_prefix="MQTT3")
        
        self.mqtt.subscribe('mqtt/test1')
        self.mqtt.subscribe('mqtt/test2')
        self.assertEqual(2, len(self.mqtt.topics))
        self.mqtt.unsubscribe_all()
        self.assertEqual(0, len(self.mqtt.topics))
        
        self.mqtt2.subscribe('mqtt2/test1')
        self.mqtt2.subscribe('mqtt2/test2')
        self.assertEqual(2, len(self.mqtt2.topics))
        self.mqtt2.unsubscribe_all()
        self.assertEqual(0, len(self.mqtt2.topics))
        
        self.mqtt3.subscribe('mqtt3/test1')
        self.mqtt3.subscribe('mqtt3/test2')
        self.assertEqual(2, len(self.mqtt3.topics))
        self.mqtt3.unsubscribe_all()
        self.assertEqual(0, len(self.mqtt3.topics))
        
        self.mqtt._disconnect()
        self.mqtt2._disconnect()
        self.mqtt3._disconnect()
    
    def test_publish_multiple_servers(self):
        self.mqtt = Mqtt(self.app, config_prefix="MQTT")
        self.mqtt2 = Mqtt(self.app, config_prefix="MQTT2")
        self.mqtt3 = Mqtt(self.app, config_prefix="MQTT3")
        
        ###### mqtt server one ######
        self.handled_message_mqtt = False
        self.handled_publish_mqtt = False
    
        @self.mqtt.on_message()
        def handle_message(client, userdata, message):
            self.handled_message_mqtt = True

        @self.mqtt.on_publish()
        def handle_publish(client, userdata, mid):
            self.handled_publish_mqtt = True

        self.mqtt.subscribe('mqtt/test')
        wait()
        self.mqtt.publish('mqtt/test', 'hello world')
        wait()

        self.assertTrue(self.handled_message_mqtt)
        self.assertTrue(self.handled_publish_mqtt)
        self.mqtt._disconnect()
        
        ###### mqtt server two ######
        self.handled_message_mqtt = False
        self.handled_publish_mqtt = False
    
        @self.mqtt2.on_message()
        def handle_message(client, userdata, message):
            self.handled_message_mqtt = True

        @self.mqtt2.on_publish()
        def handle_publish(client, userdata, mid):
            self.handled_publish_mqtt = True

        self.mqtt2.subscribe('mqtt2/test')
        wait()
        self.mqtt2.publish('mqtt2/test', 'hello world')
        wait()

        self.assertTrue(self.handled_message_mqtt)
        self.assertTrue(self.handled_publish_mqtt)
        self.mqtt2._disconnect()
        
        ###### mqtt server two ######
        self.handled_message_mqtt = False
        self.handled_publish_mqtt = False
    
        @self.mqtt3.on_message()
        def handle_message(client, userdata, message):
            self.handled_message_mqtt = True

        @self.mqtt3.on_publish()
        def handle_publish(client, userdata, mid):
            self.handled_publish_mqtt = True

        self.mqtt3.subscribe('mqtt3/test')
        wait()
        self.mqtt3.publish('mqtt3/test', 'hello world')
        wait()

        self.assertTrue(self.handled_message_mqtt)
        self.assertTrue(self.handled_publish_mqtt)
        self.mqtt3._disconnect()

    def test_logging_multiple_servers(self):
        self.mqtt = Mqtt(self.app, config_prefix="MQTT")
        self.mqtt2 = Mqtt(self.app, config_prefix="MQTT2")
        self.mqtt3 = Mqtt(self.app, config_prefix="MQTT3")

        @self.mqtt.on_log()
        def handle_logging(client, userdata, level, buf):
            self.assertIsNotNone(client)
            self.assertIsNotNone(level)
            self.assertIsNotNone(buf)
        
        @self.mqtt2.on_log()
        def handle_logging(client, userdata, level, buf):
            self.assertIsNotNone(client)
            self.assertIsNotNone(level)
            self.assertIsNotNone(buf)
        
        @self.mqtt3.on_log()
        def handle_logging(client, userdata, level, buf):
            self.assertIsNotNone(client)
            self.assertIsNotNone(level)
            self.assertIsNotNone(buf)

        self.mqtt.publish('mqtt/test', 'hello mqtt')
        self.mqtt.publish('mqtt2/test', 'hello mqtt2')
        self.mqtt.publish('mqtt3/test', 'hello mqtt3')
    
        self.mqtt._disconnect()
        self.mqtt2._disconnect()
        self.mqtt3._disconnect()
    
    def test_disconnect_multiple_servers(self):
        self.mqtt = Mqtt()
        self.mqtt2 = Mqtt()
        self.mqtt3 = Mqtt()
        self.connected = False
        
        ###### mqtt server one ######
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
        
        ###### mqtt server two ######
        @self.mqtt2.on_connect()
        def handle_connect(*args, **kwargs):
            self.connected = True

        @self.mqtt2.on_disconnect()
        def handle_disconnect(*args, **kwargs):
            self.connected = False
        
        self.assertFalse(self.connected)
        self.mqtt2.init_app(self.app, config_prefix="MQTT2")
        wait()
        self.assertTrue(self.connected)
        self.mqtt2._disconnect()
        wait()
        self.assertFalse(self.connected)
        
        ###### mqtt server one ######
        @self.mqtt3.on_connect()
        def handle_connect(*args, **kwargs):
            self.connected = True

        @self.mqtt3.on_disconnect()
        def handle_disconnect(*args, **kwargs):
            self.connected = False
        
        self.assertFalse(self.connected)
        self.mqtt3.init_app(self.app, config_prefix="MQTT3")
        wait()
        self.assertTrue(self.connected)
        self.mqtt3._disconnect()
        wait()
        self.assertFalse(self.connected)
    
if __name__ == "__main__":
    unittest.main()
    