# Syntax=docker/dockerfile:1.4@sha256:9ba7531bd80fb0a858632727cf7a112fbfd19b17e94c4e84ced81e24ef1a0dbc
FROM debian:trixie-slim@sha256:4e401d95de7083948053197a9c3913343cd06b706bf15eb6a0c3ccd26f436a0e

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nano \
    python3 \
    python3-pip \
    python3-venv \
    python3-poetry \
    graphviz \
    redis-server \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN npm install -g @mariozechner/pi-coding-agent

RUN echo "cd /workspace; \$(poetry env activate)" >> /root/.profile

WORKDIR /workspace

EXPOSE 8000 8885 8886 8887 6379 3000
