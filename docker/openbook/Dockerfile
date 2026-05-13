#===============================================================================
# Python build container
#===============================================================================
ARG PYTHON_IMAGE=python:3.12-slim@sha256:ec948fa5f90f4f8907e89f4800cfd2d2e91e391a4bce4a6afa77ba265bc3a2fe
ARG NODE_IMAGE=node:24-alpine@sha256:d1b3b4da11eefd5941e7f0b9cf17783fc99d9c6fc34884a665f40a06dbdfc94f

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

COPY bin/frontend ./bin
COPY bin/library ./bin
COPY bin/_esbuild.js ./bin

COPY package*.json ./

COPY src/libraries ./src
COPY src/frontend ./src

RUN npm run install
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
