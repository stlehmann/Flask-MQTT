from setuptools import setup
from flask_mqtt import __version__


setup(
    name='Flask-MQTT',
    version=__version__,
    url='https://github.com/MrLeeh/Flask-MQTT',
    license='MIT',
    author='Stefan Lehmann',
    author_email='stefan.st.lehmann@gmail.com',
    description='Flask extension for the MQTT protocol',
    packages=['flask_mqtt'],
    platforms='any',
    install_requires=[
        'Flask',
        'paho-mqtt'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)