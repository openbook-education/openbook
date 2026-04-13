#===============================================================================
# Python build container
#===============================================================================
ARG PYTHON_IMAGE=python:3.12-slim@sha256:804ddf3251a60bbf9c92e73b7566c40428d54d0e79d3428194edf40da6521286
ARG NODE_IMAGE=node:24-alpine@sha256:01743339035a5c3c11a373cd7c83aeab6ed1457b55da6a69e014a95ac4e4700b

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
COPY . .

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
COPY _docker/openbook/entrypoint.sh src/entrypoint.sh
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
