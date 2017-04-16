# Flask-MQTT

Flask Extension for the MQTT protocol

## Installation

Simply install the package as usual via pip:

```python
$ pip install flask-mqtt
```

## Usage

### Basic Setup

```python
from flask import Flask
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'http://mybroker.com'
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
