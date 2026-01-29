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


Configure TLS/SSL for Cloud Brokers
------------------------------------
When using cloud-hosted MQTT brokers like HiveMQ Cloud, AWS IoT, or similar services,
you typically need to enable TLS encryption. Here's how to configure Flask-MQTT for
secure connections:

::

    import ssl
    from flask import Flask
    from flask_mqtt import Mqtt

    app = Flask(__name__)
    app.config['MQTT_BROKER_URL'] = 'your-broker.your-region.aws.iot.com'  # Cloud broker URL
    app.config['MQTT_BROKER_PORT'] = 8883  # default port for TLS-enabled MQTT
    app.config['MQTT_USERNAME'] = 'your_username'
    app.config['MQTT_PASSWORD'] = 'your_password'
    app.config['MQTT_KEEPALIVE'] = 60
    app.config['MQTT_TLS_ENABLED'] = True  # Enable TLS
    app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLSv1_2  # Use TLS v1.2 (or ssl.PROTOCOL_TLS for auto-negotiate)
    app.config['MQTT_TLS_INSECURE'] = False  # Verify server certificate (keep False for production)

    mqtt = Mqtt(app)

**For HiveMQ Cloud specifically:**

::

    import ssl
    from flask import Flask
    from flask_mqtt import Mqtt

    app = Flask(__name__)
    app.config['MQTT_BROKER_URL'] = 'your-cluster.hivemq.cloud'
    app.config['MQTT_BROKER_PORT'] = 8883
    app.config['MQTT_USERNAME'] = 'your_username'
    app.config['MQTT_PASSWORD'] = 'your_password'
    app.config['MQTT_TLS_ENABLED'] = True
    app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLSv1_2  # HiveMQ Cloud requires TLS v1.2 or higher

    mqtt = Mqtt(app)

**Common cloud broker ports:**

- Port ``1883`` - Unencrypted MQTT (not recommended for cloud)
- Port ``8883`` - Encrypted MQTT with TLS
- Port ``8884`` - MQTT over WebSockets with TLS

For detailed TLS configuration options, see the :doc:`configuration` section.


Subscribe to a topic
--------------------
To subscribe to a topic simply use :py:func:`flask_mqtt.Mqtt.subscribe`.

::

    mqtt.subscribe('home/mytopic')

If you want to subscribe to a topic right from the start make sure to wait with
the subscription until the client is connected to the broker. Use the
:py:func:`flask_mqtt.Mqtt.on_connect` decorator for this.

.. important::
    To avoid race conditions where the MQTT connection is established before
    your event handlers are registered, you should initialize the MQTT client
    **after** registering all event handlers. Use the factory pattern with
    :py:func:`flask_mqtt.Mqtt.init_app` instead of passing the app directly
    to the constructor.

::

    from flask import Flask
    from flask_mqtt import Mqtt

    app = Flask(__name__)
    mqtt = Mqtt()  # Create without app

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('home/mytopic')

    mqtt.init_app(app)  # Initialize after registering handlers

To handle the subscribed messages you can define a handling function by
using the :py:func:`flask_mqtt.Mqtt.on_message` decorator.

::

    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        data = dict(
            topic=message.topic,
            payload=message.payload.decode()
        )

Subscribe to multiple topics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To subscribe to multiple topics, simply call :py:func:`flask_mqtt.Mqtt.subscribe`
multiple times with different topic names:

::

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('home/temperature')
        mqtt.subscribe('home/humidity')
        mqtt.subscribe('home/pressure')

You can also use MQTT wildcards to subscribe to multiple topics with a single
subscription:

::

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('home/#')  # Subscribe to all topics under home/
        mqtt.subscribe('sensors/+/temperature')  # Subscribe to temperature from all sensors

**MQTT wildcard patterns:**

- ``#`` (multi-level wildcard) - Matches any number of levels. Must be last character.
  
  - ``home/#`` matches ``home/kitchen``, ``home/kitchen/temp``, ``home/bedroom/humidity``

- ``+`` (single-level wildcard) - Matches exactly one level.
  
  - ``home/+/temperature`` matches ``home/kitchen/temperature``, ``home/bedroom/temperature``
  - Does not match ``home/temperature`` or ``home/kitchen/sensor/temperature``

**Handling messages from multiple topics:**

The ``on_message()`` decorator receives all messages from all subscribed topics. You can
check the topic in your handler to process different topics differently:

::

    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        topic = message.topic
        payload = message.payload.decode()
        
        if topic == 'home/temperature':
            print(f'Temperature: {payload}')
        elif topic == 'home/humidity':
            print(f'Humidity: {payload}')
        elif topic.startswith('sensors/'):
            sensor_id = topic.split('/')[1]
            print(f'Sensor {sensor_id}: {payload}')

Alternatively, you can use topic-specific callbacks by passing a topic parameter to
the decorator:

::

    @mqtt.on_message('home/temperature')
    def handle_temperature(client, userdata, message):
        print(f'Temperature: {message.payload.decode()}')
    
    @mqtt.on_message('home/humidity')
    def handle_humidity(client, userdata, message):
        print(f'Humidity: {message.payload.decode()}')


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
    
    
    @socketio.on('unsubscribe_all')
    def handle_unsubscribe_all():
        mqtt.unsubscribe_all()


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
        socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)


Using Flask-MQTT with SocketIO
-------------------------------

Flask-MQTT works well with `Flask-SocketIO`_ for real-time communication. However,
there are important considerations when combining these two extensions:

**Important configuration notes:**

1. **Always disable the reloader**:
   
   Even if you're using ``debug=True``, always set ``use_reloader=False`` when using
   Flask-MQTT. The reloader spawns multiple Flask instances, causing Flask-MQTT to
   connect multiple times and leading to unpredictable behavior.

   ::

       socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)

2. **Handle broker connection timeouts**:

   If you get a ``TimeoutError`` when initializing ``mqtt = Mqtt(app)``, it may mean:

   - The broker is not running or not accessible at the configured URL/port
   - The network connection is slow or unstable
   - The broker is rejecting the connection

   **Solution**: Use the factory pattern to defer connection until after the app context
   is properly set up, and add error handling:

   ::

       from flask import Flask, current_app
       from flask_mqtt import Mqtt

       app = Flask(__name__)
       mqtt = Mqtt()  # Create without app initially

       @mqtt.on_connect()
       def handle_connect(client, userdata, flags, rc):
           if rc == 0:
               current_app.logger.info('MQTT connected successfully')
               mqtt.subscribe('home/mytopic')
           else:
               current_app.logger.error(f'MQTT connection failed with code {rc}')

       # Initialize after all handlers are registered
       try:
           mqtt.init_app(app)
       except Exception as e:
           app.logger.warning(f'Failed to initialize MQTT: {e}')

3. **Avoid eventlet conflicts**:

   If you use ``eventlet.monkey_patch()`` with Flask-SocketIO, be aware it may interfere
   with MQTT client socket operations. Test your configuration thoroughly. If you experience
   issues, try removing the monkey patch or using a different async worker.

4. **Keep broker connection stable**:

   Configure appropriate keepalive and reconnect settings:

   ::

       app.config['MQTT_KEEPALIVE'] = 60  # seconds between pings to broker
       app.config['MQTT_CLEAN_SESSION'] = True  # clean session on connect


Troubleshooting MQTT Connection Errors
---------------------------------------

When connecting to or publishing to an MQTT broker, you may encounter error messages
with numeric codes. Here are the common MQTT error codes and their meanings:

.. tabularcolumns:: |p{3cm}|p{11.5cm}|

====== ====================================================================
Error  Description
====== ====================================================================
0      Success - No error
1      Connection refused, incorrect protocol version
2      Connection refused, invalid client identifier
3      Connection refused, server unavailable
4      Connection refused, bad username or password
5      Connection refused, not authorized
6-255  Reserved for future use
====== ====================================================================

**Common troubleshooting steps:**

1. **Error 4 (Bad username or password)**
   
   - Verify your broker credentials in your Flask configuration
   - Check that ``MQTT_USERNAME`` and ``MQTT_PASSWORD`` are correctly set
   - Ensure the credentials match what the broker expects
   - If the broker doesn't require authentication, leave username and password empty

   ::

       app.config['MQTT_USERNAME'] = 'your_username'
       app.config['MQTT_PASSWORD'] = 'your_password'

2. **Cannot connect to broker**

   - Verify the broker URL and port are correct
   - Check that the broker is running and accessible
   - For remote brokers, ensure network connectivity and firewall rules allow the connection
   - Test connectivity manually: ``telnet broker_url broker_port``

   ::

       app.config['MQTT_BROKER_URL'] = 'mqtt.example.com'
       app.config['MQTT_BROKER_PORT'] = 1883

3. **Errors during publish/subscribe**

   - Ensure the MQTT client is connected before publishing or subscribing
   - Use the ``@mqtt.on_connect()`` callback to only subscribe/publish after connection
   - Check topic names for typos or invalid characters
   - Verify broker permissions allow your client to publish/subscribe to the topic

   ::

       @mqtt.on_connect()
       def handle_connect(client, userdata, flags, rc):
           if rc == 0:  # Connection successful
               mqtt.subscribe('home/mytopic')
           else:
               print(f'Failed to connect, return code {rc}')

4. **Use logging to diagnose issues**

   Enable MQTT logging to get detailed connection and error information:

   ::

       @mqtt.on_log()
       def handle_logging(client, userdata, level, buf):
           print(f'MQTT Log [{level}]: {buf}')


Using Flask-MQTT with Application Servers (uWSGI, Gunicorn)
-----------------------------------------------------------

When deploying Flask-MQTT with production application servers, you must be careful
with process and worker configuration.

**Critical configuration requirements:**

1. **Use only one worker/process**

   Flask-MQTT maintains a single persistent MQTT connection. If multiple workers
   try to share this connection, it will lead to connection failures and timeouts.
   
   For **uWSGI**::

       [uwsgi]
       processes = 1
       single-interpreter = true

   For **Gunicorn**::

       gunicorn --workers=1 app:app

2. **Increase MQTT_KEEPALIVE for cloud brokers**

   Cloud brokers like The Things Stack, HiveMQ Cloud, and AWS IoT often close
   connections with low keepalive values. Set a reasonable keepalive interval:

   ::

       app.config['MQTT_KEEPALIVE'] = 60  # default is often too low (5-10 seconds)

   The error of repeated "Sending PINGREQ" / "Receiving PINGRESP" followed by
   connection drops is usually caused by a keepalive value that's too aggressive
   for the broker.

3. **Alternative: Use paho-mqtt directly for webhook scenarios**

   If you need to handle occasional webhooks and send MQTT commands, consider using
   paho-mqtt directly instead of Flask-MQTT. This avoids the complexity of maintaining
   a persistent connection across multiple requests:

   ::

       import paho.mqtt.client as mqttClient
       import ssl

       def publish_mqtt_command(broker, port, username, password, topic, payload):
           client = mqttClient.Client()
           client.username_pw_set(username, password=password)
           client.tls_set(ca_certs='ca.pem', certfile=None, keyfile=None,
                         cert_reqs=ssl.CERT_REQUIRED,
                         tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
           client.connect(broker, port=port)
           client.loop_start()
           client.publish(topic, payload)
           time.sleep(1)  # Allow publish to complete
           client.disconnect()
           client.loop_stop()

       @app.route('/api/webhook', methods=['POST'])
       def webhook():
           cmd = parse_webhook_data(request)
           if cmd:
               publish_mqtt_command(
                   broker='mqtt.example.com',
                   port=8883,
                   username='user',
                   password='pass',
                   topic='device/command',
                   payload=cmd
               )
           return ("OK", 200)

   This pattern creates a new client for each command, avoiding connection state issues.

4. **Check broker logs for timeout errors**

   If you see repeated errors on the broker side like ``read tcp ... i/o timeout``,
   this indicates the client is not maintaining the connection properly. Common causes:

   - Too many worker processes trying to use the same MQTT connection
   - MQTT_KEEPALIVE value too low for the broker
   - Reloader enabled, creating multiple Flask instances
   - Eventlet or other async patches interfering with socket operations


Debugging
---------

When debugging Flask-MQTT applications, you may encounter threading-related errors
such as ``greenlet.error: cannot switch to a different thread``. This occurs because
Flask-MQTT runs the MQTT client in a background thread, and debuggers pause the main
thread at breakpoints. When the background thread attempts to communicate or switch
greenlets while the main thread is frozen, this error is raised.

**Solutions for debugging:**

1. **Use logging instead of breakpoints**: Replace debugger breakpoints with logging
   statements to track application behavior without freezing threads.

   ::

       @mqtt.on_message()
       def handle_mqtt_message(client, userdata, message):
           print(f"Message received: {message.payload.decode()} on topic {message.topic}")
           # Use logging instead of setting breakpoints here
           current_app.logger.debug(f"MQTT message: {message.topic}")

2. **Use a remote debugger**: Tools like PyCharm's remote debugging or using ``remote-pdb``
   can help avoid thread conflicts by connecting via a socket rather than directly
   pausing the process.

3. **Test without the debugger**: Run the application normally (``python app.py``) to
   verify MQTT functionality works, then debug specific Flask routes separately.

4. **Disable MQTT temporarily**: For debugging Flask routes not related to MQTT, you can
   temporarily comment out MQTT initialization to debug without threading complications.

5. **Use conditional initialization**: Initialize MQTT only when not debugging:

   ::

       import os
       from flask import Flask
       from flask_mqtt import Mqtt

       app = Flask(__name__)
       mqtt = Mqtt()

       if not os.environ.get('FLASK_DEBUG'):
           mqtt.init_app(app)


.. _Flask application object: https://flask.palletsprojects.com/en/stable/api/#application-object
.. _Flask-SocketIO: https://flask-socketio.readthedocs.io/en/latest/

