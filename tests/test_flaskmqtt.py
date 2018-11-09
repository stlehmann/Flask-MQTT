import sys
import unittest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from flask import Flask


# apply mock
sys.modules['paho.mqtt.client'] = MagicMock()
try:
    sys.modules.pop('flask_mqtt')
except KeyError:
    pass


import flask_mqtt  # noqa: E402
Mqtt = flask_mqtt.Mqtt


class FlaskMQTTTestCase(unittest.TestCase):

    def setUp(self):
        sys.modules['paho.mqtt.client'] = MagicMock()
        self.app = Flask(__name__)

    def test_early_initialization_app_is_not_none(self):
        mqtt = Mqtt(self.app)
        self.assertIsNotNone(mqtt.app)

    def test_late_initialization_app_is_none(self):
        mqtt = Mqtt()
        mqtt.init_app(self.app)
        self.assertIsNone(mqtt.app)

    def test_mqtt_config_values(self):
        self.app.config['MQTT_USERNAME'] = 'username'
        self.app.config['MQTT_PASSWORD'] = 'password'
        self.app.config['MQTT_BROKER_URL'] = 'broker_url'
        self.app.config['MQTT_BROKER_PORT'] = 'broker_port'
        self.app.config['MQTT_TLS_ENABLED'] = 'tls_enabled'
        self.app.config['MQTT_KEEPALIVE'] = 'keepalive'
        self.app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
        self.app.config['MQTT_LAST_WILL_MESSAGE'] = 'last will'
        self.app.config['MQTT_LAST_WILL_QOS'] = 2
        self.app.config['MQTT_LAST_WILL_RETAIN'] = True
        self.app.config['MQTT_TLS_CA_CERTS'] = 'tls_ca_certs'
        self.app.config['MQTT_TLS_CERTFILE'] = 'tls_certfile'
        self.app.config['MQTT_TLS_KEYFILE'] = 'tls_keyfile'
        self.app.config['MQTT_TLS_CERT_REQS'] = 'tls_cert_reqs'
        self.app.config['MQTT_TLS_VERSION'] = 'tls_version'
        self.app.config['MQTT_TLS_CIPHERS'] = 'tls_ciphers'
        self.app.config['MQTT_TLS_INSECURE'] = 'tls_insecure'

        mqtt = Mqtt(self.app)

        self.assertEqual('username', mqtt.username)
        self.assertEqual('password', mqtt.password)
        self.assertEqual('broker_url', mqtt.broker_url)
        self.assertEqual('broker_port', mqtt.broker_port)
        self.assertEqual('tls_enabled', mqtt.tls_enabled)
        self.assertEqual('keepalive', mqtt.keepalive)
        self.assertEqual('home/lastwill', mqtt.last_will_topic)
        self.assertEqual('last will', mqtt.last_will_message)
        self.assertEqual(2, mqtt.last_will_qos)
        self.assertEqual(True, mqtt.last_will_retain)
        self.assertEqual('tls_ca_certs', mqtt.tls_ca_certs)
        self.assertEqual('tls_certfile', mqtt.tls_certfile)
        self.assertEqual('tls_keyfile', mqtt.tls_keyfile)
        self.assertEqual('tls_cert_reqs', mqtt.tls_cert_reqs)
        self.assertEqual('tls_version', mqtt.tls_version)
        self.assertEqual('tls_ciphers', mqtt.tls_ciphers)
        self.assertEqual('tls_insecure', mqtt.tls_insecure)

        # values passed to paho mqtt
        mqtt.client.username_pw_set.assert_called_once_with('username',
                                                            'password')

        mqtt.client.tls_set.called_once_with(
            ca_certs='tls_ca_certs',
            certfile='tls_certfile',
            keyfile='tls_keyfile',
            cert_reqs='tls_cert_reqs',
            tls_version='tls_version',
            ciphers='tls_ciphers',
        )

    def test_connect_disconnect(self):
        mqtt = Mqtt(self.app)
        self.assertEqual(1, mqtt.client.loop_start.call_count)
        self.assertEqual(1, mqtt.client.connect.call_count)
        mqtt._disconnect()
        self.assertEqual(1, mqtt.client.disconnect.call_count)


if __name__ == '__main__':
    unittest.main()
