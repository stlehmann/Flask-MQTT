# Flask-MQTT

Flask Extension for the [MQTT protocol][1]. Basically it is a thin wrapper
around [paho-mqtt][0] and aims to simplify MQTT integration in Flask. MQTT is a
machine-to-machine "Internet of Things" protocol and was designed for extremely
lightweight publish/subscribe messaging transport.

[![Inactively Maintained](https://img.shields.io/badge/Maintenance%20Level-Inactively%20Maintained-yellowgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![Documentation Status](https://readthedocs.org/projects/flask-mqtt/badge/?version=latest)](https://flask-mqtt.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/Flask-MQTT.svg)](https://badge.fury.io/py/Flask-MQTT)
[![CI](https://github.com/stlehmann/Flask-MQTT/actions/workflows/ci.yml/badge.svg)](https://github.com/stlehmann/Flask-MQTT/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/stlehmann/Flask-MQTT/badge.svg?branch=master)](https://coveralls.io/github/stlehmann/Flask-MQTT?branch=master)
[![Downloads](https://pepy.tech/badge/flask-mqtt)](https://pepy.tech/project/flask-mqtt)
[![Downloads](https://pepy.tech/badge/flask-mqtt/week)](https://pepy.tech/project/flask-mqtt/week)

Find the documentation on [https://flask-mqtt.readthedocs.io][2].

## Features

* configuration via Flask config variables
* auto-connect on start of your web application
* publish and subscribe messages
* connect to multiple MQTT servers
* use callbacks for certain topics
* use one callback for all subscribed topics

## Limitations

Flask-MQTT was developed to provide an easy-to-setup solution for interacting
with IoT devices. A typical scenario would be a Raspberry Pi running a
mosquitto mqtt server combined with a Flask webserver.

### Multiple workers

**Flask-MQTT is currently not suitable for the use with multiple worker
instances.** So if you use a WSGI server like *gevent* or *gunicorn* make sure
you only have one worker instance.

### Reloader

Make sure to disable Flasks autoreloader. If activated it spawns two
instances of a Flask application. This leads to the same problems as multiple
workers. To prevent Flask-MQTT from running code twice it is necessary to
deactivate the automatic reloader.

## Installation

Simply install the package as usual via pip:

```bash
$ pip install flask-mqtt
```

Or with conda from the conda-forge channel:

```bash
$ conda config --add channels conda-forge
$ conda install flask-mqtt
```

## Usage

### Basic Setup

```python
from flask import Flask
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'mybroker.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'user'
app.config['MQTT_PASSWORD'] = 'secret'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

@app.route('/')
def index():
    return render_template('index.html')

```

### Subscribe to a topic

To subscribe to a topic simply use `mqtt.subscribe()`. To make sure the
subscription gets handled correctly on startup place the subscription inside
an `on_connect()` callback function.

**Important:** To avoid race conditions where the MQTT connection might be established before your event handlers are registered, initialize the MQTT client **after** registering all event handlers:

```python
from flask import Flask
from flask_mqtt import Mqtt

app = Flask(__name__)
mqtt = Mqtt()  # Create without app

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('home/mytopic')

mqtt.init_app(app)  # Initialize after registering handlers
```

To handle the subscribed messages you can define a handling function by
decorating it with `@mqtt.on_message()`.

```python
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
```

To unsubscribe do:

```python
mqtt.unsubscribe('home/mytopic')
```

Or if you want to unsubscribe all topics use `unsubscribe_all()`.

```python
mqtt.unsubscribe_all()
```

### Publish

To publish a message you can use the `publish()` method.

```python
mqtt.publish('home/mytopic', 'this is my message')
```

### Connect to multiple MQTT Servers

To connect to multiple servers, you can create multiple mqtt clients in your application by specifying the ```config_prefix``` when initializing ```Mqtt()```

```python
# default mqtt client
app.config["MQTT_broker_url"] = "example.com"
app.config["MQTT_broker_port"] = 8883
mqtt = Mqtt(app)

# create second mqtt client for a different broker 
app.config["MQTT2_broker_url"] = "example2.com"
app.config["MQTT_broker_port"] = 1883
mqtt2 = Mqtt(app, config_prefix="MQTT2")

# create third mqtt client for a different broker 
app.config["MQTT3_broker_url"] = "example3.com"
app.config["MQTT3_broker_port"] = 1885
mqtt3 = Mqtt(app, config_prefix="MQTT3")
```

### Small publish/subscribe MQTT client
Note: if you want to enable ssl transport layer on the mqtt communication
take a look at the commented sections in the example file.
You may need to add or replace some of the MQTT_TLS options and adjust to your needs.

```python
"""

A small Test application to show how to use Flask-MQTT.

"""

import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
# if SSL enabled
# from flask_mqtt import ssl

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
app.config['MQTT_CLEAN_SESSION'] = True

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

# Parmeters for SSL with client certificate
# app.config['MQTT_TLS_ENABLED']   = True
# app.config['MQTT_BROKER_URL']    = 'test.mosquitto.org'
# app.config['MQTT_BROKER_PORT']   = 8884
# app.config['MQTT_TLS_INSECURE']  = False
# app.config['MQTT_TLS_CA_CERTS']  = 'mosquitto.org.crt'
# app.config['MQTT_TLS_CERTFILE']  = 'client.crt'
# app.config['MQTT_TLS_KEYFILE']   = 'client.key'
# app.config['MQTT_TLS_VERSION']   = ssl.PROTOCOL_TLSv1_2
# app.config['MQTT_TLS_CERT_REQS'] = True

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
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)

```

[0]: https://github.com/eclipse/paho.mqtt.python
[1]: https://mqtt.org/
[2]: https://flask-mqtt.readthedocs.io/en/latest/
