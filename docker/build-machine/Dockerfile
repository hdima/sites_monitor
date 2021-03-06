FROM ubuntu

RUN apt-get -y update \
    && apt-get -y install sudo \
    && apt-get -y install less \
    && apt-get -y install python3 \
    && apt-get -y install python3-pip \
    && apt-get -y clean

RUN pip3 install coverage \
    && pip3 install mypy \
    && pip3 install lxml

VOLUME /build
WORKDIR /build

COPY entrypoint.sh /usr/local/sbin/

RUN chmod a+x /usr/local/sbin/entrypoint.sh

ENTRYPOINT ["/usr/local/sbin/entrypoint.sh"]
