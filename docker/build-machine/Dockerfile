FROM ubuntu

RUN apt-get -y update \
    && apt-get -y install sudo \
    && apt-get -y install less \
    && apt-get -y install zip \
    && apt-get -y install python3 \
    && apt-get -y install python3-pip \
    && apt-get -y clean

RUN pip3 install coverage \
    && pip3 install mypy \
    && pip3 install lxml \
    && pip3 install pyyaml \
    && pip3 install confluent-kafka \
    && pip3 install psycopg2-binary

VOLUME /build
WORKDIR /build

COPY entrypoint.sh /usr/local/sbin/

RUN chmod a+x /usr/local/sbin/entrypoint.sh

ENTRYPOINT ["/usr/local/sbin/entrypoint.sh"]
