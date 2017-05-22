Configuration
=============

The following configuration keys exist for Flask-MQTT. Flask-MQTT loads these
values from your main Flask config.

Configuration Keys
------------------

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

============================== ================================================
``MQTT_BROKER_URL``            The broker URL that should be used for the
                               connection. Defaults to ``localhost``.
                               Example:

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

``MQTT_REFRESH_TIME``          The refresh interval in seconds used to check
                               for pending messages. Defaults to 1.0 seconds.

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
============================== ================================================
