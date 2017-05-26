# Flask-MQTT

Flask Extension for the [MQTT protocol][1]. Basically it is a thin wrapper
around [paho-mqtt][0] and aimes to simplify MQTT integration in Flask. MQTT is a
machine-to-machine "Internet of Things" protocol and was designed for extremely
lightweight publish/subscribe messaging transport.

[![Documentation Status](https://readthedocs.org/projects/flask-mqtt/badge/?version=latest)](http://flask-mqtt.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/Flask-MQTT.svg)](https://badge.fury.io/py/Flask-MQTT)

Find the documentation on [http://flask-mqtt.readthedocs.io][2].

## Features

* configuration via Flask config variables
* auto-connect on start of your web application
* publish and subscribe messages
* use callbacks for certain topics
* use one callback for all subscribed topics

## Todo

* auto-reconnect after broker went down

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

To subscribe to a topic simply use `mqtt.subscribe()`.

```python
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

[0]: https://github.com/eclipse/paho.mqtt.python
[1]: http://mqtt.org/
[2]: http://flask-mqtt.readthedocs.io/en/latest/
