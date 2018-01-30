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

If you want to subscribe to a topic right from the start make sure to wait with
the subscription until the client is connected to the broker. Use the
:py:func:`flask_mqtt.Mqtt.on_connect` decorator for this.

::

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
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
Flask-MQTT plays nicely with the `Flask-SocketIO`_ extension. Flask-SocketIO
gives Flask applications access to low latency bi-directional communications
between the clients and the server. So it is ideal for displaying live data,
state changes or alarms that get in via MQTT. Have a look at the example to
see Flask-MQTT and Flask-SocketIO play together. The example provides a small
publish/subscribe client using Flask-SocketIO to insantly show subscribed
messages and publish messages.


::

    """

    A small Test application to show how to use Flask-MQTT.

    """

    import eventlet
    import json
    from flask import Flask, render_template
    from flask_mqtt import Mqtt
    from flask_socketio import SocketIO
    from flask_bootstrap import Bootstrap

    eventlet.monkey_patch()

    app = Flask(__name__)
    app.config['SECRET'] = 'my secret key'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_USERNAME'] = ''
    app.config['MQTT_PASSWORD'] = ''
    app.config['MQTT_KEEPALIVE'] = 5
    app.config['MQTT_TLS_ENABLED'] = False

    # Parameters for SSL enabled
    # app.config['MQTT_BROKER_PORT'] = 8883
    # app.config['MQTT_TLS_ENABLED'] = True
    # app.config['MQTT_TLS_INSECURE'] = True
    # app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

    mqtt = Mqtt(app)
    socketio = SocketIO(app)
    bootstrap = Bootstrap(app)


    @app.route('/')
    def index():
        return render_template('index.html')


    @socketio.on('publish')
    def handle_publish(json_str):
        data = json.loads(json_str)
        mqtt.publish(data['topic'], data['message'])


    @socketio.on('subscribe')
    def handle_subscribe(json_str):
        data = json.loads(json_str)
        mqtt.subscribe(data['topic'])


    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        data = dict(
            topic=message.topic,
            payload=message.payload.decode()
        )
        socketio.emit('mqtt_message', data=data)


    @mqtt.on_log()
    def handle_logging(client, userdata, level, buf):
        print(level, buf)


    if __name__ == '__main__':
        socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)


.. _Flask application object: http://flask.pocoo.org/docs/0.12/api/#application-object
.. _Flask-SocketIO: https://flask-socketio.readthedocs.io/en/latest/

