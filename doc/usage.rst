Usage
=====

Connect to a broker
-------------------
To connect to a broker you only need to initialize the `Flask-MQTT` extension
with your `Flask application`. You can do this by directly passing the `Flask
application object`_ on object creation.

::

    from flask import Flask
    from flask_mqtt import Mqtt

    app = Flask(__name__)
    mqtt = Mqtt(app)

The *Flask-MQTT* extension supports the factory pattern so you can instantiate
a ``Mqtt`` object without an app object. Use the ``init_app()`` function inside
the factory function for initialization.

::

    from flask import Flask
    from flask_mqtt import Mqtt

    mqtt = Mqtt()

    def create_app():
        app = Flask(__name__)
        mqtt.init_app(app)

Configure the MQTT client
-------------------------
The configuration of the MQTT client is done via configuration variables as 
it is common for Flask extension.

::

    from flask import Flask
    from flask_mqtt import Mqtt


    app = Flask(__name__)
    app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'  # use the free broker from HIVEMQ
    app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
    app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
    app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
    app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
    app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

    mqtt = Mqtt()

All available configuration variables are listed in the configuration section.


Subscribe to a topic
--------------------
To subscribe to a topic simply use :py:func:`flask_mqtt.Mqtt.subscribe`.

::

    mqtt.subscribe('home/mytopic')

To handle the subscribed messages you can define a handling function by
using the :py:func:`flask_mqtt.Mqtt.on_message` decorator.

::

    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        data = dict(
            topic=message.topic,
            payload=message.payload.decode()
        )

To unsubscribe use :py:func:`flask_mqtt.Mqtt.unsubscribe`.

::

    mqtt.unsubscribe('home/mytopic')

Or if you want to unsubscribe all topics use
:py:func:`flask_mqtt.Mqtt.unsubscribe_all`.

::

    mqtt.unsubscribe_all()


Publish a message
-----------------
Publishing a message is easy. Just use the :py:func:`flask_mqtt.Mqtt.publish`
method here.

::

    mqtt.publish('home/mytopic', 'hello world')


Logging
-------
To enable logging there exists the :py:func:`flask_mqtt.Mqtt.on_log` decorator.
The level variable gives the severity of the message and will be one of these:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

======================================== ============
:py:obj:`flask_mqtt.MQTT_LOG_INFO`        0x01

:py:obj:`flask_mqtt.MQTT_LOG_NOTICE`      0x02

:py:obj:`flask_mqtt.MQTT_LOG_WARNING`     0x04

:py:obj:`flask_mqtt.MQTT_LOG_ERR`         0x08

:py:obj:`flask_mqtt.MQTT_LOG_DEBUG`       0x10
======================================== ============

::

    @mqtt.on_log()
    def handle_logging(client, userdata, level, buf):
        if level == MQTT_LOG_ERR:
            print('Error: {}'.format(buf))

Interact with SocketIO
----------------------

.. _Flask application object: http://flask.pocoo.org/docs/0.12/api/#application-object
