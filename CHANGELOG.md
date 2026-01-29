# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## **1.3.0**

### Added
- support for paho-mqtt 2.0
- [#192](https://github.com/stlehmann/Flask-MQTT/pull/192) support for Python 3.14
- [#151](https://github.com/stlehmann/Flask-MQTT/commit/90b11435a32e059a40aa1eccb18f0f32d3351b48) pass disconnect properties to disconnect handler 
- [#195](https://github.com/stlehmann/Flask-MQTT/commit/9bd89bd9edad131e27e9ef437cd3602dac878288) documentation to avoid race conditions
- [#198](https://github.com/stlehmann/Flask-MQTT/pull/198) update documentation for paho-mqtt 2.0 changes and TLS support

### Changed
- [#193](https://github.com/stlehmann/Flask-MQTT/pull/193) update dependencies and compatibility to paho-mqtt 2.0
- [#189](https://github.com/stlehmann/Flask-MQTT/issues/189) fix documenation build issue 

### Removed
- [#192](https://github.com/stlehmann/Flask-MQTT/pull/192) drop support for Python <3.10

## **1.2.0**

### Added
* Github action for continuous integration. 

    The workflow installs Python dependencies, run tests and lint with a single version of Python
    For more information see: https://help.github.com/actions/language-and-framework-guides/using-python-with-github-actions

* connect to multiple MQTT servers

    Added support for connecting to multiple MQTT servers. For more information, follow this [link](https://github.com/stlehmann/Flask-MQTT/blob/d362514245c98cd57a301341c88c5cebb6a2a52b/README.md?plain=1#L127)

### Changed

* [Test coverage and CI integration for multiple MQTT servers](https://github.com/stlehmann/Flask-MQTT/commit/c7be57c54f99d7fbbde76b7e4a8eed48c4ae60d3)

* Function enhancement for [`unsubscribe_all()`](https://github.com/stlehmann/Flask-MQTT/commit/e86a22084138ee7615e46c951ad01647a2db0315)

* [Fixed topic population in subscribe() for tuple/list type topics](https://github.com/stlehmann/Flask-MQTT/commit/9d6c2e99db769476f08a3c6cfdaf9bbc6ddca2f2)

* [correction on init_app()](https://github.com/stlehmann/Flask-MQTT/commit/f889437de6a1cbef2cde093c1f94d3785a43d179)
    
    `Mqtt.init_app(self, app: Flask, ···)` now assigns `app` to `self.app` if this one is None.

* Dependabot updates
### Removed

## **1.1.2**

### Added

### Changed
* fixed issue [#76](https://github.com/stlehmann/Flask-MQTT/issues/76) 
* [#77](https://github.com/stlehmann/Flask-MQTT/pull/77) Pass client id to MQTT client

### Removed

## **1.1.1**

### Added

### Changed

### Removed
* [#43](https://github.com/stlehmann/Flask-MQTT/issues/43) Remove reconnect for
publish function. If you want to reconnect to server check the return value for
MQTT_ERR_NO_CONN and call reconnect function.

## **1.1.0**
* drop support for Python 2.7 and Python <= 3.5
* use type-annotations and variable type annotations
* include mypy type check in travis ci

## **1.0.7**
* optional support for async mqtt loop
* include Python 3.7 and 3.8 in ci

## **1.0.6**
* do not install typing when using Python >= 3.5 [cekk]
* omit verbose logging messages

## **1.0.5**
* fix issue #40. One can now use the @mqtt decorators before calling `mqtt.init_app()`
* fix problems with continuous integration on Travis CI

## **1.0.4**
* complete coverage with type annotations
* add logging
* update Pipfile and add requirements.txt
* add limitation hint in the documentation and readme

## **1.0.2**
* nothing special

## **1.0.1**
* Establish Flake8 conformity

## **0.0.11**
* add websockets support
* fix bug with qos subscriptions

## **0.0.10**
* add `on_connect` and `on_disconnect` decorators

## **0.0.8**
* add last will to be published on client disconnect
* add `on_publish`, `on_subscribe` and `on_unsubscribe` decorator

## **0.0.7**
* 100% test coverage
* bugfix: make flask application object at initialization optional again
* proper disconnecting on mqtt._disconnect

## **0.0.6**
* Flask-MQTT now supports Python 2.7

## **0.0.5**
* fixed unsupported type annotations for older Python 3 versions

## **0.0.4**
* documentation improvements
* support Python 3 versions < 3.6 by installing typing package

## **0.0.3**
* automatic reconnect
* instant auto-refresh
* set keepalive time in seconds
* logging decorator

## **0.0.2**
* add SSL/TLS support
