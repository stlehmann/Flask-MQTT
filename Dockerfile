FROM python:3.10
RUN apt-get update -y
RUN apt-get install -y mosquitto
COPY . /app
WORKDIR /app
RUN pip3 install -e .
RUN pip3 install pytest coverage pytest-cov
RUN py3clean .
CMD mosquitto -d && pytest -v --cov flask_mqtt