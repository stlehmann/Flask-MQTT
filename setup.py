import os
import sys
from setuptools import setup


if sys.argv[-1] == 'test':
    os.system('coverage run -m unittest discover -s tests')
    os.system('coverage html --include flask_mqtt/*')
    os.system('coverage report --include flask_mqtt/*')
else:
    setup(
        name='Flask-MQTT',
        version='0.0.5',
        url='https://github.com/MrLeeh/Flask-MQTT',
        license='MIT',
        author='Stefan Lehmann',
        author_email='stefan.st.lehmann@gmail.com',
        description='Flask extension for the MQTT protocol',
        packages=['flask_mqtt'],
        platforms='any',
        install_requires=[
            'Flask',
            'typing',
            'paho-mqtt'
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )
