#
# Docker image containing data-producer.py and data-consumer.py
#
FROM ubuntu:latest
MAINTAINER wenzhe "xwzusa@gmail.com"

RUN apt-get update
RUN apt-get install -y python3 python3-pip wget
COPY ./data-producer.py /
COPY ./data-consumer.py /
COPY ./requirements.txt /
RUN pip3 install -r requirements.txt

# RUN vs CMD: https://stackoverflow.com/a/37462208
CMD python3 data-producer.py BTC-USD test kafka:9092