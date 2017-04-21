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

============================== ================================================