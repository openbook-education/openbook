#===============================================================================
# Python build container
#===============================================================================
ARG PYTHON_IMAGE=python:3.12-slim@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9
ARG NODE_IMAGE=node:24-alpine@sha256:a0b9bf06e4e6193cf7a0f58816cc935ff8c2a908f81e6f1a95432d679c54fbfd

FROM ${PYTHON_IMAGE} AS python-build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MSGPACK_PUREPYTHON 1

WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .

RUN python -m venv .env
RUN .env/bin/pip install poetry poetry-plugin-export
RUN .env/bin/poetry export --format=requirements.txt --output=requirements.txt

#===============================================================================
# Frontend build container
#===============================================================================
FROM ${NODE_IMAGE} AS nodejs-build

WORKDIR /app

COPY bin/frontend ./bin/frontend
COPY bin/library ./bin/library
COPY bin/_esbuild.js ./bin/

COPY package*.json ./

COPY src/libraries ./src/libraries
COPY src/frontend ./src/frontend

RUN npm ci
RUN npm run build:libraries
RUN npm run build:frontend

#===============================================================================
# App container
#===============================================================================
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MSGPACK_PUREPYTHON 1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p src/_media.volume; \
    mkdir -p src/_static.volume; \
    mkdir -p src/_static; \
    mkdir -p src/_media

COPY --from=python-build /app/requirements.txt .
RUN python -m venv .env
RUN .env/bin/pip install -r requirements.txt
RUN .env/bin/pip install psycopg

COPY . .
COPY docker/openbook/entrypoint.sh src/entrypoint.sh
RUN chmod +x src/entrypoint.sh

# Copy frontend files to ./_static and ./_media.
# entrypoint.sh then copies the files onto the volumes ./_static.volume and ./_media.volume.
COPY --from=nodejs-build /app/src/_media src/_media
COPY --from=nodejs-build /app/src/_static src/_static

# This copies to ./_static, according to settings.py.
# entrypoint.sh then copies the files onto the volume ./_static.volume.
RUN .env/bin/python src/manage.py collectstatic --noinput

VOLUME /app/src/_media.volume
VOLUME /app/src/_static.volume
EXPOSE 8000

WORKDIR /app/src
ENTRYPOINT ["./entrypoint.sh"]
