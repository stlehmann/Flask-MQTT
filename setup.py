"""Flask-MQTT Setup."""
import io
import re
import os
import sys
from setuptools import setup


def read(*names, **kwargs):
    """Open a file and read its content."""
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    """Find current package version number."""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


long_description = read('README.md')


if sys.argv[-1] == 'test':
    os.system('coverage run -m unittest discover -s tests')
    os.system('coverage html --include flask_mqtt/*')
    os.system('coverage report -m --include flask_mqtt/*')
else:
    setup(
        name='Flask-MQTT',
        version=find_version('flask_mqtt', '__init__.py'),
        url='https://github.com/MrLeeh/Flask-MQTT',
        license='MIT',
        author='Stefan Lehmann',
        author_email='stefan.st.lehmann@gmail.com',
        description='Flask extension for the MQTT protocol',
        long_description=long_description,
        long_description_content_type='text/markdown',
        packages=['flask_mqtt'],
        platforms='any',
        install_requires=[
            'Flask',
            'typing',
            'paho-mqtt'
        ],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )
