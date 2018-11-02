Changelog
=========

Version 1.0.5
-------------
* fix issue #40. One can now use the @mqtt decorators before calling `mqtt.init_app()`
* fix problems with continuous integration on Travis CI

Version 1.0.4
-------------
* complete coverage with type annotations
* add logging
* update Pipfile and add requirements.txt
* add limitation hint in the documentation and readme

Version 1.0.2
-------------
* nothing special

Version 1.0.1
-------------
* Establish Flake8 conformity

Version 0.0.11
--------------
* add websockets support
* fix bug with qos subscriptions

Version 0.0.10
--------------
* add `on_connect` and `on_disconnect` decorators

Version 0.0.8
-------------
* add last will to be published on client disconnect
* add `on_publish`, `on_subscribe` and `on_unsubscribe` decorator

Version 0.0.7
-------------
* 100% test coverage
* bugfix: make flask application object at initialization optional again
* proper disconnecting on mqtt._disconnect

Version 0.0.6
-------------
* Flask-MQTT now supports Python 2.7

Version 0.0.5
-------------
* fixed unsupported type annotations for older Python 3 versions

Version 0.0.4
-------------
* documentation improvements
* support Python 3 versions < 3.6 by installing typing package

Version 0.0.3
-------------
* automatic reconnect
* instant auto-refresh
* set keepalive time in seconds
* logging decorator

Version 0.0.2
-------------
* add SSL/TLS support
