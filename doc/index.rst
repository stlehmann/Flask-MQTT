.. Flask-MQTT documentation master file, created by
   sphinx-quickstart on Mon Apr 17 10:26:02 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-MQTT's documentation!
======================================

Flask-MQTT is a `Flask <http://flask.pocoo.org/>`_ extension meant to facilitate
the integration of a MQTT client into your web application. Basically it is a
thin wrapper around the `paho-mqtt`_ package to simplify MQTT integration in
a Flask application.
`MQTT <http://mqtt.org/>`_ is a machine-to-machine (M2M)/"Internet of Things"
(IoT) protocol which is designed as a lightweight publish/subscribe messaging
transport. It comes very handy when trying to connect multiple IoT devices with each other
or monitor and control these devices from one or multiple clients.

.. toctree::
   :maxdepth: 2

   configuration
   usage
   changelog
   api/index

Support
=======
This package uses type annotations so it needs Python 3.6 or Python 2.7/3.x 
with the `typing package <https://pypi.python.org/pypi/typing>`_ installed.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _paho-mqtt: https://github.com/eclipse/paho.mqtt.python
