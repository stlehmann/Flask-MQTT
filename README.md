# Flask-MQTT

Flask Extension for the [MQTT protocol][1]. Basically it is a thin wrapper
around [paho-mqtt][0] and aimes to simplify MQTT integration in Flask. MQTT is a
machine-to-machine "Internet of Things" protocol and was designed for extremely
lightweight publish/subscribe messaging transport.

[![Documentation Status](https://readthedocs.org/projects/flask-mqtt/badge/?version=latest)](http://flask-mqtt.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/Flask-MQTT.svg)](https://badge.fury.io/py/Flask-MQTT) [![Travis CI](https://travis-ci.org/stlehmann/Flask-MQTT.svg?branch=master)](https://travis-ci.org/stlehmann/Flask-MQTT.svg?branch=master)

Find the documentation on [http://flask-mqtt.readthedocs.io][2].

## Features

* configuration via Flask config variables
* auto-connect on start of your web application
* publish and subscribe messages
* use callbacks for certain topics
* use one callback for all subscribed topics

## Limitations

**Flask-MQTT is currently not suitable for the use with multiple worker
instances.** So if you use a WSGI server like *gevent* or *gunicorn* make sure
you only have one worker instance.

## Installation

Simply install the package as usual via pip:

```bash
$ pip install flask-mqtt
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

```python
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('home/mytopic')
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

### Small publish/subscribe MQTT client

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

```

[0]: https://github.com/eclipse/paho.mqtt.python
[1]: http://mqtt.org/
[2]: http://flask-mqtt.readthedocs.io/en/latest/
