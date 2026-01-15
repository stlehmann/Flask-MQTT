FROM python:3.13
RUN apt-get update \
 && apt-get install -y --no-install-recommends mosquitto \
 && rm -rf /var/lib/apt/lists/*
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -e . \
 && pip install --no-cache-dir pytest coverage pytest-cov
RUN py3clean .
CMD sh -c "\
  mosquitto -p 1883 -d && \
  mosquitto -p 1885 -d && \
  mosquitto -p 1886 -d && \
  pytest -v --cov=flask_mqtt \
"
