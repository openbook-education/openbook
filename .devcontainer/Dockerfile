# Syntax=docker/dockerfile:1.4
FROM debian:trixie-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nano \
    python3 \
    python3-pip \
    python3-venv \
    python3-poetry \
    redis-server \
    nodejs \
    npm \
    openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN npm install -g @mariozechner/pi-coding-agent

RUN echo "cd /workspace; $(poetry env activate)" >> /root/.profile

WORKDIR /workspace

EXPOSE 8000 8885 8886 8887 6379 3000
