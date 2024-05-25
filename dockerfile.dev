FROM docker.uclv.cu/python:3.8

COPY pip.conf pip.conf
ENV PIP_CONFIG_FILE pip.conf

COPY requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt
