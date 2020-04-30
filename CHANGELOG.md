# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 1.1.1

### Added

### Changed

### Removed
* [#43](https://github.com/stlehmann/Flask-MQTT/issues/43) Remove reconnect for
publish function. If you want to reconnect to server check the return value for
MQTT_ERR_NO_CONN and call reconnect function.

## 1.1.0
* drop support for Python 2.7 and Python <= 3.5
* use type-annotations and variable type annotations
* include mypy type check in travis ci

## 1.0.7
* optional support for async mqtt loop
* include Python 3.7 and 3.8 in ci

## ## ## ## ## ## ## ## ## 1.0.6
* do not install typing when using Python >= 3.5 [cekk]
* omit verbose logging messages

## 1.0.5
* fix issue #40. One can now use the @mqtt decorators before calling `mqtt.init_app()`
* fix problems with continuous integration on Travis CI

## 1.0.4
* complete coverage with type annotations
* add logging
* update Pipfile and add requirements.txt
* add limitation hint in the documentation and readme

## 1.0.2
* nothing special

## 1.0.1
* Establish Flake8 conformity

## 0.0.11
* add websockets support
* fix bug with qos subscriptions

## 0.0.10
* add `on_connect` and `on_disconnect` decorators

## 0.0.8
* add last will to be published on client disconnect
* add `on_publish`, `on_subscribe` and `on_unsubscribe` decorator

## 0.0.7
* 100% test coverage
* bugfix: make flask application object at initialization optional again
* proper disconnecting on mqtt._disconnect

## 0.0.6
* Flask-MQTT now supports Python 2.7

## 0.0.5
* fixed unsupported type annotations for older Python 3 versions

## 0.0.4
* documentation improvements
* support Python 3 versions < 3.6 by installing typing package

## 0.0.3
* automatic reconnect
* instant auto-refresh
* set keepalive time in seconds
* logging decorator

## 0.0.2
* add SSL/TLS support
