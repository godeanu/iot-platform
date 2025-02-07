FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir "paho-mqtt<2.0"


COPY data_generator.py .

CMD ["python", "data_generator.py"]
