FROM ubuntu:xenial
RUN apt-get update -y
RUN apt-get install -y mosquitto python3 python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install -e .
RUN pip3 install pytest coverage pytest-cov
RUN py3clean .
CMD mosquitto -d && pytest -v --cov flask_mqtt