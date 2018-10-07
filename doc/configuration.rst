Configuration
=============

The following configuration keys exist for Flask-MQTT. Flask-MQTT loads these
values from your main Flask config.

Configuration Keys
------------------

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

============================== ================================================
``MQTT_CLIENT_ID``             the unique client id string used when connecting
                               to the broker. If client_id is zero length or
                               None, then one will be randomly generated.

``MQTT_BROKER_URL``            The broker URL that should be used for the
                               connection. Defaults to ``localhost``. Example:

                               - ``mybroker.com``

``MQTT_BROKER_PORT``           The broker port that should be used for the
                               connection. Defaults to 1883.

                               - MQTT: ``1883``
                               - MQTT encrypted (SSL): ``8883``

``MQTT_USERNAME``              The username used for authentication. If none is
                               provided authentication is disabled. Defaults to
                               ``None``.

``MQTT_PASSWORD``              The password used for authentication. Defaults
                               to ``None``. Only needed if a username is
                               provided.

``MQTT_KEEPALIVE``             Maximum period in seconds between communications
                               with the broker. If no other messages are being
                               exchanged, this controls the rate at which the
                               client will send ping messages to the broker.
                               Defaults to 60 seconds.

``MQTT_TLS_ENABLED``           Enable TLS for the connection to the MQTT broker.
                               Use the following config keys to configure TLS.

``MQTT_TLS_CA_CERTS``          A string path to the Certificate Authority
                               certificate files that are to be treated as
                               trusted by this client. Required.

``MQTT_TLS_CERTFILE``          String pointing to the PEM encoded client
                               certificate. Defaults to None.

``MQTT_TLS_KEYFILE``           String pointing to the PEM encoded client
                               private key. Defaults to None.

``MQTT_TLS_CERT_REQS``         Defines the certificate requirements that the
                               client imposes on the broker. By default this
                               is ssl.CERT_REQUIRED, which means that the
                               broker must provide a certificate. See the
                               ssl pydoc for more information on this
                               parameter. Defaults to ssl.CERT_REQUIRED.

``MQTT_TLS_VERSION``           Specifies the version of the SSL/TLS protocol
                               to be used. By default TLS v1 is used.
                               Previous versions (all versions beginning with
                               SSL) are possible but not recommended due to
                               possible security problems.
                               Defaults to ssl.PROTOCOL_TLSv1.

``MQTT_TLS_CIPHERS``           A string specifying which encryption ciphers
                               are allowable for this connection, or None
                               to use the defaults. See the ssl pydoc for
                               more information. Defaults to None.

``MQTT_TLS_INSECURE``          Configure verification of the server hostname
                               in the server certificate. Defaults to False.
                               Do not use this function in a real system.
                               Setting value to True means there is no
                               point using encryption.

``MQTT_LAST_WILL_TOPIC``       The topic that the will message should be
                               published on. If not set no will message will
                               be sent on disconnecting the client.

``MQTT_LAST_WILL_MESSAGE``     The message to send as a will. If not given, or
                               set to None a zero length message will be used
                               as the will. Passing an int or float will result
                               in the payload being converted to a string
                               representing that number. If you wish to send
                               a true int/float, use struct.pack() to
                               create the payload you require.

``MQTT_LAST_WILL_QOS``         The quality of service level to use for the will.
                               Defaults to 0.

``MQTT_LAST_WILL_RETAIN``      If set to true, the will message will be set
                               as the "last known good"/retained message for
                               the topic. Defaults to False.

``MQTT_TRANSPORT``             set to "websockets" to send MQTT over
                               WebSockets. Leave at the default of "tcp" to
                               use raw TCP.

``MQTT_PROTOCOL_VERSION``      The version of the MQTT protocol to use. Can be
                               either ``MQTTv31`` or ``MQTTv311`` (default).
============================== ================================================
