import sys
import unittest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from flask import Flask

from paho.mqtt import client as real_client
from paho.mqtt.client import (
    CallbackAPIVersion as RealCallbackAPIVersion,
    ConnackCode,
    ConnectFlags,
    DisconnectFlags,
    MQTTErrorCode,
    convert_connack_rc_to_reason_code,
    convert_disconnect_error_code_to_reason_code,
)
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.reasoncodes import ReasonCode

# apply mock, keeping the real callback API helpers
mock_mqtt = MagicMock()
for _name in (
    "CallbackAPIVersion", "ConnackCode", "MQTTErrorCode", "MQTTv5", "MQTT_ERR_SUCCESS",
    "convert_connack_rc_to_reason_code", "convert_disconnect_error_code_to_reason_code",
):
    setattr(mock_mqtt, _name, getattr(real_client, _name))
sys.modules['paho.mqtt.client'] = mock_mqtt
try:
    sys.modules.pop('flask_mqtt')
except KeyError:
    pass


import flask_mqtt  # noqa: E402
Mqtt = flask_mqtt.Mqtt


class FlaskMQTTTestCase(unittest.TestCase):

    def setUp(self):
        # Clear the module cache and create a fresh mock
        try:
            sys.modules.pop('flask_mqtt')
        except KeyError:
            pass
        
        mock_mqtt = MagicMock()
        for _name in (
            "CallbackAPIVersion", "ConnackCode", "MQTTErrorCode", "MQTTv5", "MQTT_ERR_SUCCESS",
            "convert_connack_rc_to_reason_code", "convert_disconnect_error_code_to_reason_code",
        ):
            setattr(mock_mqtt, _name, getattr(real_client, _name))
        sys.modules['paho.mqtt.client'] = mock_mqtt
        self.mock_mqtt = mock_mqtt

        # Re-import to get fresh Mqtt class with new mock
        import flask_mqtt
        global Mqtt
        Mqtt = flask_mqtt.Mqtt
        
        self.app = Flask(__name__)

    def test_early_initialization_app_is_not_none(self):
        mqtt = Mqtt(self.app)
        self.assertIsNotNone(mqtt.app)

    def test_late_initialization_app_is_not_none(self):
        mqtt = Mqtt()
        mqtt.init_app(self.app)
        self.assertIsNotNone(mqtt.app)

    def test_mqtt_config_values(self):
        self.app.config['MQTT_USERNAME'] = 'username'
        self.app.config['MQTT_PASSWORD'] = 'password'
        self.app.config['MQTT_BROKER_URL'] = 'broker_url'
        self.app.config['MQTT_BROKER_PORT'] = 'broker_port'
        self.app.config['MQTT_TLS_ENABLED'] = 'tls_enabled'
        self.app.config['MQTT_CLEAN_SESSION'] = False
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
        self.assertEqual(False, mqtt.clean_session)
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

        mqtt.client.tls_set.assert_called_once_with(
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

    def test_connect_async(self):
        mqtt = Mqtt(self.app, connect_async=True)
        self.assertEqual(1, mqtt.client.loop_start.call_count)
        self.assertEqual(1, mqtt.client.connect_async.call_count)
        mqtt._disconnect()
        self.assertEqual(1, mqtt.client.disconnect.call_count)

    def test_tls_insecure(self):
        self.app.config['MQTT_TLS_ENABLED'] = True
        self.app.config['MQTT_TLS_INSECURE'] = True
        mqtt = Mqtt(self.app)
        # Check that tls_insecure_set was called with True
        mqtt.client.tls_insecure_set.assert_called_with(True)

    def test_on_disconnect_handler_receives_parameters(self):
        """Test that disconnect handler receives client, userdata, and rc parameters."""
        mqtt = Mqtt(self.app)
        
        # Create a mock handler
        mock_handler = MagicMock()
        
        # Register the handler using decorator
        @mqtt.on_disconnect()
        def handle_disconnect(client, userdata, rc):
            mock_handler(client, userdata, rc)
        
        # Simulate a disconnect event
        mock_client = MagicMock()
        mock_userdata = {'test': 'data'}
        mock_rc = 0
        
        mqtt._handle_disconnect(
            mock_client, mock_userdata, DisconnectFlags(False), ReasonCode(PacketTypes.DISCONNECT, identifier=mock_rc), None
        )
        
        # Verify the handler was called with the correct parameters
        mock_handler.assert_called_once_with(mock_client, mock_userdata, mock_rc)

    def test_on_disconnect_handler_not_called_when_none(self):
        """Test that no error occurs when disconnect happens without a handler."""
        mqtt = Mqtt(self.app)
        
        # Simulate a disconnect event without a registered handler
        mock_client = MagicMock()
        mock_userdata = {'test': 'data'}
        mock_rc = 0
        
        # This should not raise an error
        mqtt._handle_disconnect(
            mock_client, mock_userdata, DisconnectFlags(False), ReasonCode(PacketTypes.DISCONNECT, identifier=mock_rc), None
        )
        
        # Verify connected status is updated
        self.assertFalse(mqtt.connected)

    def test_on_disconnect_sets_connected_to_false(self):
        """Test that _handle_disconnect sets connected to False."""
        mqtt = Mqtt(self.app)
        mqtt.connected = True
        
        mock_client = MagicMock()
        mock_userdata = None
        mock_rc = 0
        
        mqtt._handle_disconnect(
            mock_client, mock_userdata, DisconnectFlags(False), ReasonCode(PacketTypes.DISCONNECT, identifier=mock_rc), None
        )
        
        self.assertFalse(mqtt.connected)

    def test_on_connect_handler_receives_parameters(self):
        """Test that connect handler receives client, userdata, flags, and rc parameters."""
        mqtt = Mqtt(self.app)
        
        # Create a mock handler
        mock_handler = MagicMock()
        
        # Register the handler using decorator
        @mqtt.on_connect()
        def handle_connect(client, userdata, flags, rc):
            mock_handler(client, userdata, flags, rc)
        
        # Simulate a successful connect event
        mock_client = MagicMock()
        mock_userdata = {'test': 'data'}
        mock_flags = {'session present': 0}
        mock_rc = 0  # MQTT_ERR_SUCCESS
        
        mqtt._handle_connect(
            mock_client, mock_userdata, ConnectFlags(False), ReasonCode(PacketTypes.CONNACK, identifier=mock_rc), None
        )
        
        # Verify the handler was called with the correct parameters
        mock_handler.assert_called_once_with(mock_client, mock_userdata, mock_flags, mock_rc)

    def test_on_connect_converts_v311_refusal_to_int(self):
        """Test that a refused v3 connack arrives as the old int and does not set connected."""
        mqtt = Mqtt(self.app)
        handler = MagicMock()
        mqtt.on_connect()(handler)
        reason = convert_connack_rc_to_reason_code(ConnackCode.CONNACK_REFUSED_NOT_AUTHORIZED)
        mqtt._handle_connect(None, None, ConnectFlags(True), reason, None)
        handler.assert_called_once_with(None, None, {"session present": 1}, 5)
        self.assertFalse(mqtt.connected)

    def test_on_subscribe_handler_receives_int_granted_qos(self):
        """Test that on_subscribe gets a tuple of ints, 0x80 for a rejected subscription."""
        mqtt = Mqtt(self.app)
        handler = MagicMock()
        mqtt.on_subscribe()(handler)
        codes = [ReasonCode(PacketTypes.SUBACK, identifier=q) for q in (0, 1, 2, 0x80)]
        mqtt._handle_subscribe(None, None, 7, codes, None)
        handler.assert_called_once_with(None, None, 7, (0, 1, 2, 128))
        granted = handler.call_args[0][3]
        self.assertTrue(all(type(q) is int for q in granted))
        self.assertTrue(any(q >= 0x80 for q in granted))

    def test_on_publish_and_unsubscribe_receive_v1_arguments(self):
        """Test that on_publish and on_unsubscribe get (client, userdata, mid)."""
        mqtt = Mqtt(self.app)
        publish, unsubscribe = MagicMock(), MagicMock()
        mqtt.on_publish()(publish)
        mqtt.on_unsubscribe()(unsubscribe)
        mqtt._handle_publish(None, None, 3, ReasonCode(PacketTypes.PUBACK), None)
        mqtt._handle_unsubscribe(None, None, 4, [], None)
        publish.assert_called_once_with(None, None, 3)
        unsubscribe.assert_called_once_with(None, None, 4)

    def test_on_disconnect_converts_error_code_to_int(self):
        """Test that an unexpected v3 disconnect arrives as MQTT_ERR_CONN_LOST (7)."""
        mqtt = Mqtt(self.app)
        handler = MagicMock()
        mqtt.on_disconnect()(handler)
        reason = convert_disconnect_error_code_to_reason_code(MQTTErrorCode.MQTT_ERR_CONN_LOST)
        mqtt._handle_disconnect(None, None, DisconnectFlags(False), reason, None)
        handler.assert_called_once_with(None, None, 7)

    def test_on_disconnect_protocol_error_matches_v1(self):
        """Test that a v3 protocol error arrives as paho VERSION1 gave it (2, or 7 on paho < 2.2)."""
        mqtt = Mqtt(self.app)
        handler = MagicMock()
        mqtt.on_disconnect()(handler)
        reason = convert_disconnect_error_code_to_reason_code(MQTTErrorCode.MQTT_ERR_PROTOCOL)
        lost = convert_disconnect_error_code_to_reason_code(MQTTErrorCode.MQTT_ERR_CONN_LOST)
        mqtt._handle_disconnect(None, None, DisconnectFlags(False), reason, None)
        handler.assert_called_once_with(None, None, 7 if reason == lost else 2)

    def test_client_uses_callback_api_version_2(self):
        """Test that the paho client is created with callback API version 2."""
        Mqtt(self.app)
        self.mock_mqtt.Client.assert_called_with(RealCallbackAPIVersion.VERSION2)

    def test_v5_connect_and_disconnect_pass_properties(self):
        """Test that v5 handlers get the ReasonCode and properties like paho VERSION1."""
        mqtt = Mqtt(self.app)
        mqtt.client.protocol = real_client.MQTTv5
        connect, disconnect = MagicMock(), MagicMock()
        mqtt.on_connect()(connect)
        mqtt.on_disconnect()(disconnect)
        ok = ReasonCode(PacketTypes.CONNACK, identifier=0)
        mqtt._handle_connect(None, None, ConnectFlags(False), ok, "props")
        connect.assert_called_once_with(None, None, {"session present": 0}, ok, "props")
        self.assertTrue(mqtt.connected)
        server = ReasonCode(PacketTypes.DISCONNECT, identifier=0x8B)
        mqtt._handle_disconnect(None, None, DisconnectFlags(True), server, "props")
        disconnect.assert_called_once_with(None, None, server, "props")
        disconnect.reset_mock()
        lost = convert_disconnect_error_code_to_reason_code(MQTTErrorCode.MQTT_ERR_CONN_LOST)
        mqtt._handle_disconnect(None, None, DisconnectFlags(False), lost, None)
        disconnect.assert_called_once_with(None, None, 7, None)

    def test_v5_subscribe_passes_reason_codes_and_properties(self):
        """Test that v5 on_subscribe gets the ReasonCode list and properties."""
        mqtt = Mqtt(self.app)
        mqtt.client.protocol = real_client.MQTTv5
        handler = MagicMock()
        mqtt.on_subscribe()(handler)
        codes = [ReasonCode(PacketTypes.SUBACK, identifier=0x80)]
        mqtt._handle_subscribe(None, None, 9, codes, "props")
        handler.assert_called_once_with(None, None, 9, codes, "props")


if __name__ == '__main__':
    unittest.main()
