FROM rickybarillas/bases:0.1.2

RUN apt-get update

RUN apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential

RUN apt-get install -y cron
RUN apt-get install -y --reinstall rsyslog

RUN pip3 install --upgrade pip

RUN mkdir -p /workdir/chips


COPY ./requirements.txt /workdir/chips

RUN pip3 install -r /workdir/chips/requirements.txt

COPY . /workdir/

WORKDIR /workdir/chips

ENTRYPOINT ["python3", "/workdir/chips/chips.py"]
