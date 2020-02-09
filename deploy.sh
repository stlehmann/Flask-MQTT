#!/usr/bin/env bash
mypy -p flask_mqtt
mosquitto -d && py.test -v --cov  flask_mqtt
