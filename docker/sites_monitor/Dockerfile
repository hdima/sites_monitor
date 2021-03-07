FROM ubuntu

RUN apt-get -y update \
    && apt-get -y install python3 \
    && apt-get -y install python3-pip \
    && apt-get -y clean

RUN pip3 install pyyaml \
    && pip3 install confluent-kafka

COPY sites_monitor.zip /usr/local/lib/

ENV PYTHONPATH /usr/local/lib/sites_monitor.zip

USER nobody
WORKDIR /opt/sites_monitor

ENTRYPOINT ["/usr/bin/python3", "-m", "sites_monitor"]
