==================
Installation Guide
==================

This page guides administrators through production deployment and validation of OpenBook. It
covers the required components, supported web-server setups, and the routine operational tasks
needed to keep an installation stable, secure, and maintainable.

.. contents:: Page Content
   :local:


-----------
Quick Start
-----------

System Overview
...............

OpenBook is a standard Django deployment with a few project-specific considerations. The general
deployment process follows the `Django documentation <https://docs.djangoproject.com/en/5.0/#the-development-process>`_.
This page focuses on the concrete parts that matter when you run OpenBook in production.

.. figure:: img/deployment-architecture.png
   :align: center
   :alt: Deployment architecture with reverse proxy, ASGI app, SQL database, and optional Redis.

   OpenBook deployment architecture and component boundaries.

The deployment can stay simple at first. A single machine can host the reverse proxy, the ASGI
application, the database, and optional supporting services. If the reverse proxy can distribute
traffic across several backend processes, the same layout also scales to multiple application
instances later.

**Front Web Server** -- A front web server is not strictly required, but it is the usual choice for
TLS termination, static file delivery, uploaded media delivery, and reverse proxying to the Django
application. In a small installation, one machine often serves all of these roles. In a larger
installation, static files, media files, and the application can be separated across domains or
machines. Apache HTTP Server remains a common production choice, while `Caddy <https://caddyserver.com/>`_
is a good modern alternative with minimal configuration.

.. code-block:: apache

   # this can go in either server config, virtual host, directory or .htaccess
   WSGIPassAuthorization On

**ASGI Server** -- The core application runs through an ASGI server. For Django projects this is
commonly `Daphne <https://github.com/django/daphne>`_, which is already part of the project
dependencies. A typical production command is:

.. code-block:: bash

   daphne -p 8000 -b 0.0.0.0 openbook.asgi:application

**Redis** -- OpenBook incroporates real-time features based on Django Channels and Celery. These
require a running Redis service to decouple the main web process from background and task runners.
While these can run on many different queues, Redis is the usual backend. The pre-defined Django
configuration expects Redis on ``localhost:6379`` by default, although you can override that in
the local settings.

**Database** -- OpenBook needs a SQL database for persistent storage. `MariaDB
<https://mariadb.org/>`_ and `PostgreSQL <https://www.postgresql.org/>`_ are both suitable
choices. Refer to the `Django database documentation
<https://docs.djangoproject.com/en/5.0/ref/databases/>`_ for supported backends, install the
matching Python driver, and update the deployment settings accordingly.

Docker Compose
..............

The :file:`docker/` directory contains a working Docker Compose example that you can use as a reference
deployment and as a starting point for your own environment. It is useful both for local deployment
tests and for understanding how the components fit together.

The most common Docker Compose commands are:

* :command:`docker compose build` to build the images
* :command:`docker compose up` to start the stack in the foreground
* :command:`docker compose up -d` to start the stack in the background
* :command:`docker compose down` to stop the stack
* :command:`docker exec -it docker-openbook-server-1 sh` to open a shell in the application container

The example setup defines the following services:

* ``postgres`` in container ``docker-postgres-1`` for persistent database storage
* ``redis`` in container ``docker-redis-1`` for asynchronous processing support
* ``openbook-server`` in container ``docker-openbook-server-1`` for the Django application
* ``webserver`` in container ``docker-webserver-1`` for the front-facing reverse proxy

There is currently no official image on Docker Hub. The repository instead provides a Dockerfile
that Compose builds locally. The legacy deployment recommendation still applies: copy the
:file:`docker/` directory to a location outside the Git checkout and adapt it to your environment.


-------------------
Manual Installation
-------------------

This tutorial walks through a complete manual installation of OpenBook on a single Debian server.
All components --- the application, database, Redis, and the front web server --- run on the same
host. The steps can be adapted to other Debian-based distributions and, with small adjustments, to
any system where the required packages are available. The following assumptions apply throughout:

* The source code is downloaded from the GitHub release page or by cloning a release branch.
* The Python environment lives under :file:`/opt/openbook` and is managed with Poetry.
* MariaDB or PostgreSQL is installed via the OS package manager.
* Redis is installed via the OS package manager.
* Background jobs run as cron tasks.
* The application and all supporting processes start automatically via SystemD.

Two front web server options are covered: Apache with Certbot for Let's Encrypt TLS, and Caddy,
which handles certificate issuance and renewal automatically.

.. note::

   Commands in this tutorial assume root access. Adapt :command:`sudo` usage to your own privilege
   model. Steps that should run as the application user call that out explicitly.

Prerequisites
.............

Before you begin, make sure the Debian server meets the following preconditions:

* A public IP address with DNS pointing to the server's hostname.
* Ports 80 and 443 reachable from the internet (required for Let's Encrypt).
* Root access or a user with :command:`sudo` privileges.
* API keys and addresses for at least one LLM provider (Mistral, OpenAPI, ...)

Install base system packages. The list covers Python 3.x, the native libraries required for SAML
support, Redis, and a database server. Choose MariaDB or PostgreSQL based on your preference:

.. code-block:: bash

   apt-get update
   apt-get install -y \
       python3 python3-venv python3-poetry \
       git \
       xmlsec1 libxmlsec1-dev libltdl-dev \
       redis-server \
       mariadb-server default-libmysqlclient-dev

.. note::

   To use PostgreSQL instead of MariaDB, install ``postgresql`` and ``libpq-dev`` in place of
   the MariaDB packages. The database driver step later in this tutorial covers both options.

System User and Application Directory
......................................

Running the application as a dedicated non-root user limits the impact of any application-level
security issue. Create the user and the directory that will hold both the source code and the
Python environment:

.. code-block:: bash

   useradd --system --shell /usr/sbin/nologin --home-dir /opt/openbook openbook
   mkdir -p /opt/openbook
   chown openbook:openbook /opt/openbook

Download the Source Code
........................

Download the latest release archive from the `GitHub releases page
<https://github.com/openbook-education/openbook/releases>`_. Each release attaches a source
archive named ``openbook-x.y.z-source.tar.gz`` --- replace ``x.y.z`` with the actual version
number. You can download it manually from the browser, or fetch it directly on the server:

.. code-block:: bash

   # Option A: release archive (downloaded with wget)
   cd /opt/openbook
   wget https://github.com/openbook-education/openbook/releases/download/vx.y.z/openbook-x.y.z-source.tar.gz
   tar -xzf openbook-x.y.z-source.tar.gz --strip-components=1
   rm openbook-x.y.z-source.tar.gz

   # Option B: Git clone of a release branch
   git clone --branch release/x.y.z https://github.com/openbook-education/openbook.git /opt/openbook

.. note::

   We recommend cloning the release branch. This greatly simplifies installation of
   patches and upgrading to newer versions.

After extracting or cloning, restore the correct ownership:

.. code-block:: bash

   chown -R openbook:openbook /opt/openbook

Set Up the Python Environment
.............................

Configure Poetry to create the virtual environment inside the project directory. This gives the
SystemD unit files a stable, predictable path to the Python interpreter:

.. code-block:: bash

   su -s /bin/bash openbook -c "
       cd /opt/openbook &&
       poetry config virtualenvs.in-project true &&
       poetry install --without dev,docs
   "

Poetry creates the virtual environment at :file:`/opt/openbook/.venv`. Next, install the database
driver that matches your chosen database server. For PostgreSQL:

.. code-block:: bash

   su -s /bin/bash openbook -c "cd /opt/openbook && .venv/bin/pip install psycopg"

For MariaDB:

.. code-block:: bash

   su -s /bin/bash openbook -c "cd /opt/openbook && .venv/bin/pip install mysqlclient"

.. note::

   If the installation fails with errors mentioning ``xmlsec`` or ``lxml``, see
   :ref:`os-dependencies-xmlsec1-ltdl` for resolution steps.

Configure the Application
.........................

Deployment-specific settings are separated from the shared codebase through a local settings
file. Copy :file:`/opt/openbook/src/local_settings.py.template` to
:file:`/opt/openbook/src/local_settings.py` and populate it with values appropriate for your
installation. It should look similar to the snippet below. Adapt the database engine, hostname,
credentials, and timezone to match your environment:

.. code-block:: python

   # /opt/openbook/src/local_settings.py

   SECRET_KEY = "replace-with-a-strong-random-value"
   DEBUG = False
   ALLOWED_HOSTS = ["openbook.example.com"]

   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.postgresql",  # or django.db.backends.mysql
           "NAME": "openbook",
           "USER": "openbook",
           "PASSWORD": "strong-database-password",
           "HOST": "localhost",
           "PORT": "5432",  # 3306 for MariaDB
       }
   }

   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [("localhost", 6379)],
           },
       },
   }

   # TODO: LLM API credentials

   STATIC_ROOT = "/opt/openbook/src/_static"
   STATIC_URL = "/static/"
   MEDIA_ROOT = "/opt/openbook/src/_media"
   MEDIA_URL = "/media/"

   USE_TZ = True
   TIME_ZONE = "Europe/Berlin"
   SITE_ID = 1

Generate a strong value for ``SECRET_KEY`` with Python:

.. code-block:: bash

   python3 -c "import secrets; print(secrets.token_urlsafe(50))"

Paste the output into the settings file, then restrict the file's permissions so that other
system users cannot read the credentials:

.. code-block:: bash

   chown openbook:openbook /opt/openbook/src/local_settings.py
   chmod 640 /opt/openbook/src/local_settings.py

.. important::

   Always use your local copy of :file:`local_settings.py.template` file as a starting point.

   Always update the secret key with a strong random value to reduce the risk of signed-cookie
   tampering, forged sessions, and CSRF token abuse. Never reuse the same key across environments.

Prepare the Database
....................

Create a dedicated database and user for OpenBook. The commands below cover MariaDB and PostgreSQL.

For MariaDB:

.. code-block:: bash

   mariadb -u root <<EOF
   CREATE USER 'openbook'@'localhost' IDENTIFIED BY 'strong-database-password';
   CREATE DATABASE openbook CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   GRANT ALL PRIVILEGES ON openbook.* TO 'openbook'@'localhost';
   FLUSH PRIVILEGES;
   EOF

For PostgreSQL:

.. code-block:: bash

   sudo -u postgres psql <<EOF
   CREATE USER openbook WITH PASSWORD 'strong-database-password';
   CREATE DATABASE openbook OWNER openbook;
   EOF

.. note::

   You can run the same command as above to generate a strong password:

   .. code-block:: bash

      python3 -c "import secrets; print(secrets.token_urlsafe(50))"

Next, run the Django migrations to create all tables:

.. code-block:: bash

   su -s /bin/bash openbook -c "
       cd /opt/openbook/src &&
       ../.venv/bin/python manage.py migrate
   "

Load initial data:

.. code-block:: bash

   su -s /bin/bash openbook -c "
       cd /opt/openbook/src &&
       ../.venv/bin/python manage.py load_initial_data
   "

Create superuser (admin user):

.. code-block:: bash

   su -s /bin/bash openbook -c "
       cd /opt/openbook/src &&
       ../.venv/bin/python manage.py createsuperuser
   "

Collect Static Files
....................

Django collects all static assets into a single directory so the web server can serve them
directly. Run this command once now, and again after every application update:

.. code-block:: bash

   su -s /bin/bash openbook -c "
       cd /opt/openbook/src &&
       ../.venv/bin/python manage.py collectstatic --no-input
   "

Create the media directory that Django uses for uploaded files:

.. code-block:: bash

   mkdir -p /opt/openbook/src/_media
   chown openbook:openbook /opt/openbook/src/_media

SystemD Services
................

Three processes need to run continuously: the Daphne ASGI server, the Channels background
worker, and Redis. Redis runs as a standard OS service. Create SystemD unit files for the
application processes.

Create :file:`/etc/systemd/system/openbook.service`:

.. code-block:: ini

   [Unit]
   Description=OpenBook ASGI Server (Daphne)
   After=network.target redis.service

   [Service]
   User=openbook
   Group=openbook
   WorkingDirectory=/opt/openbook/src
   ExecStart=/opt/openbook/.venv/bin/daphne -p 8000 openbook.asgi:application
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

Create :file:`/etc/systemd/system/openbook-worker.service`:

.. code-block:: ini

   [Unit]
   Description=OpenBook Background Worker
   After=network.target redis.service

   [Service]
   User=openbook
   Group=openbook
   WorkingDirectory=/opt/openbook/src
   ExecStart=/opt/openbook/.venv/bin/python manage.py runworker default
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

.. note::

   The source tree contains two template files you can copy and adapt. Instead of directly
   creating the files inside :file:`/etc/systemd/system/` you can symlink them from the
   OpenBook source directory.

Enable and start all services:

.. code-block:: bash

   systemctl daemon-reload
   systemctl enable --now redis openbook openbook-worker

Verify that all three services are active:

.. code-block:: bash

   systemctl status redis openbook openbook-worker

Front Web Server: Caddy
.......................

Caddy is a modern and performant alternative to traditional Apache web server setups.
Advantages are increased throughput, simpler configuration and automatic provisioning
of Let's Encrypt certificates without any additional tooling.

.. seealso::

   See the next section, if you prefer Apache.

Install Caddy directly from the Debian package repository:

.. code-block:: bash

   apt-get install -y caddy

Replace the default :file:`/etc/caddy/Caddyfile` with the following:

.. code-block:: text

   openbook.example.com {
       # Serve static and uploaded media files directly:
       handle /static/* {
           root * /opt/openbook/src
           file_server
       }
       handle /media/* {
           root * /opt/openbook/src
           file_server
       }

       # Proxy all other requests to Daphne:
       handle {
           reverse_proxy localhost:8000
       }
   }

Enable and start Caddy:

.. code-block:: bash

   systemctl enable --now caddy

Caddy detects the configured hostname, requests a certificate from Let's Encrypt on first
startup, and schedules automatic renewal. No further TLS configuration is required.

Front Web Server: Apache With Certbot
......................................

OpenBook runs perfectly fine with the traditional Apache web server. If you prefer this
option over Caddy, install Apache and the Certbot plugin with the following commands.

.. code-block:: bash

   apt-get install -y apache2 certbot python3-certbot-apache
   a2enmod proxy proxy_http proxy_wstunnel headers ssl rewrite

Next, create a virtual host configuration in
:file:`/etc/apache2/sites-available/openbook.conf`:

.. code-block:: apache

   <VirtualHost *:80>
       ServerName openbook.example.com
       RewriteEngine On
       RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
   </VirtualHost>

   <VirtualHost *:443>
       ServerName openbook.example.com
       SSLEngine On
       # Certbot fills in the certificate paths after issuance.

       # Required for DRF token authentication through the proxy:
       WSGIPassAuthorization On

       # Serve static and uploaded media files directly:
       Alias /static/ /opt/openbook/src/_static/
       Alias /media/  /opt/openbook/src/_media/
       <Directory /opt/openbook/src/_static>
           Require all granted
       </Directory>
       <Directory /opt/openbook/src/_media>
           Require all granted
       </Directory>

       # WebSocket upgrade for Django Channels:
       RewriteEngine On
       RewriteCond %{HTTP:Upgrade} websocket [NC]
       RewriteRule /(.*) ws://127.0.0.1:8000/$1 [P,L]

       # Reverse proxy all other requests to Daphne:
       ProxyPreserveHost On
       ProxyPass /static/ !
       ProxyPass /media/  !
       ProxyPass / http://127.0.0.1:8000/
       ProxyPassReverse / http://127.0.0.1:8000/
   </VirtualHost>

Enable the site and obtain a Let's Encrypt certificate:

.. code-block:: bash

   a2ensite openbook
   systemctl reload apache2
   certbot --apache -d openbook.example.com

Certbot writes the certificate paths into the virtual host and reloads Apache automatically.
Renewal runs via a pre-installed systemd timer and requires no additional configuration.

Periodic Maintenance With Cron
..............................

A few Django management commands should run on a regular schedule to keep the deployment clean.
Add the following entries to the ``openbook`` user's crontab:

.. code-block:: bash

   crontab -u openbook -e

Append these lines to the crontab:

.. code-block:: text

   # Remove expired sessions every night at 02:00
   0 2 * * * cd /opt/openbook/src && /opt/openbook/.venv/bin/python manage.py clearsessions

   # Remove stale content types every night at 02:15
   15 2 * * * cd /opt/openbook/src && /opt/openbook/.venv/bin/python manage.py remove_stale_contenttypes --no-input

   # Daily database backup at 03:00
   0 3 * * * cd /opt/openbook/src && /opt/openbook/.venv/bin/python manage.py dbbackup

.. seealso::

   :ref:`periodic-jobs` and :ref:`backup-commands` list all available management commands and
   backup configuration options.

Final Testing
.............

After the deployment is complete, verify that the full stack works end to end before handing the
system over to users.

Start with service health checks on the server:

.. code-block:: bash

   systemctl status redis openbook openbook-worker
   systemctl status caddy   # or: systemctl status apache2

All units should be in ``active (running)`` state.

Then open the OpenBook URL in a browser (for example ``https://openbook.example.com``) and test
the most important paths:

* The landing page loads without a 5xx error.
* :file:`/api/` responds through the reverse proxy.
* Static assets (CSS/JS) are loaded correctly.
* Uploaded media files are reachable when opened directly.

Next, sign in with the superuser account created earlier and validate core administrative actions:

* Open the Django admin and verify that model lists render.
* Create and save a small test object.
* Trigger one action that creates a background task and confirm no worker errors appear.

While testing, keep an eye on logs in a second terminal:

.. code-block:: bash

   journalctl -u openbook -u openbook-worker -u redis -f
   journalctl -u caddy -f   # or: journalctl -u apache2 -f

If pages load, login works, and no recurring errors appear in the logs, the installation is ready
for production traffic.

.. admonition:: Congratulations

   You made it until the end. Your OpenBook installation should now be ready. Join our community
   to learn about new features and updates as well as to share your experiences.

---------------
Troubleshooting
---------------

.. _os-dependencies-xmlsec1-ltdl:

OS Dependencies (xmlsec1, ltdl)
...............................

Before you install Python dependencies with :command:`poetry install`, make sure the required system
packages for SAML support are present. On Linux, install them through your distribution package
manager.

* ``xmlsec1`` including development headers
* ``libtool-ltdl`` including development headers

These packages are required for SAML integration. If you do not plan to use SAML and cannot install
them, you can edit :file:`pyproject.toml` and remove ``"saml"`` from the ``django-allauth`` dependency
extras.

If the server later crashes with ``xmlsec.InternalError: (-1, 'lxml & xmlsec libxml2 library
version mismatch')``, the cause is usually one of the following:

* The system has multiple ``libxml2`` versions installed.
* ``lxml`` and ``xmlsec`` were compiled against different ``libxml2`` versions.
* ``libxml2``, ``lxml``, or ``xmlsec`` changed without rebuilding the others.
* Poetry installed binary wheels that do not match the system libraries.

In many cases, reinstalling both packages from source resolves the mismatch::
In many cases, reinstalling both packages from source resolves the mismatch:

.. code-block:: bash

   poetry run pip uninstall lxml xmlsec -y
   poetry run pip install --no-binary=:all: lxml xmlsec


Local Django Settings
.....................

Deployment-specific configuration is separated from the shared Django settings through a local
override file. This keeps must-have settings, required to run OpenBook at all, in version control
while defining a clear place for database connections, credentials and other site-specific settings.

.. list-table:: Periodic Management Commands
   :header-rows: 1
   :width: 100%

   * - File
     - User Changeable
     - Content
   * - :file:`settings.py`
     - No
     - Core Django settings
   * - :file:`local_settings.py`
     - Yes
     - Installation-specific settings, e.g. database connections

The :file:`local_settings.py` file is therefore excluded from version control. A template file in the
repository documents the settings that administrators commonly need to adjust.

WSGI vs. ASGI
.............

Traditional WSGI deployments with Apache and mod_python are not sufficient here because OpenBook
also relies on Django Channels and therefore expects an ASGI-capable application server. Daphne is
already included, so the basic startup command is straightforward.

To start the application and listen on all interfaces::
To start the application and listen on all interfaces:

.. code-block:: bash

   cd src
   daphne -p 8000 -b 0.0.0.0 openbook.asgi:application

On a local workstation you may need to run Daphne through Poetry so it uses the project virtual
environment.

If the application sits behind a reverse proxy on the same host, bind it to localhost instead:

.. code-block:: bash

   cd src
   daphne -p 8000 openbook.asgi:application

If you still need a reverse proxy, `Caddy <https://caddyserver.com/>`_ is a practical option.

Do not forget static and uploaded media files. By default, OpenBook stores them in :file:`_static/` and
:file:`_media/` within the Django project, although the file system paths and public URLs can be
overridden in :file:`local_settings.py`. After changing static asset settings, collect the files before
serving them:

.. code-block:: bash

   python ./manage.py collectstatic

Authorization Headers
.....................

When the web server proxies API requests, make sure it forwards authorization headers. The `Django
REST framework authentication guide <https://www.django-rest-framework.org/api-guide/authentication/#apache-mod_wsgi-specific-configuration>`_
notes that Apache with mod_wsgi does not pass the ``Authorization`` header by default. In that
case, enable it explicitly:

.. _periodic-jobs:

Periodic Jobs
.............

OpenBook includes Django management commands that should run periodically to keep the deployment
clean and predictable. In practice you would call them through cron, a systemd timer, or another
job scheduler.

The commands are typically run from the Django project directory::
The commands are typically run from the Django project directory:

.. code-block:: bash

   ./manage.py command --options

The most important periodic tasks are listed below.

.. list-table:: Periodic Management Commands
   :header-rows: 1
   :width: 100%

   * - Management Command
     - Description
   * - :command:`clearsessions`
     - Removes expired sessions from the database.
   * - :command:`remove_stale_contenttypes --no-input`
     - Removes stale content types for non-existing models.

.. _backup-commands:

Backup Commands
...............

OpenBook includes `Django DBBackups <https://django-dbbackup.readthedocs.io/>`_ for database and
media backups. Backups can be written to local storage or to remote destinations such as S3 or
Dropbox. The upstream project documentation covers the full configuration model. The table below
summarizes the commands that administrators use most often.

.. list-table:: Backup Management Commands
   :header-rows: 1
   :width: 100%

   * - Management Command
     - Description
   * - :command:`dbbackup`
     - Creates a new database backup.
   * - :command:`dbrestore`
     - Restores a database backup into an empty database.
   * - :command:`listbackups`
     - Lists the available backups.
   * - :command:`mediabackup`
     - Creates a backup of uploaded media files.
   * - :command:`mediarestore`
     - Restores uploaded media files from backup storage.

The target database should be empty before you restore a backup. For larger installations, the
DBBackups documentation recommends creating backups from a database replica to reduce load on the
primary database server.

SAML SSO and Social Login
.........................

OpenBook uses `django-allauth[saml]
<https://docs.allauth.org/en/latest/socialaccount/providers/saml.html>`_ for SAML identity
providers. The same authentication stack can also support local user registration and common social
login providers such as Google or Microsoft. A few project-specific hints are documented in
:file:`local_settings.py`, but the `django-allauth documentation
<https://docs.allauth.org/en/latest/index.html>`_ remains the authoritative reference.

If you load the initial test data, the system already contains a dummy SAML provider based on
`mocksaml.com <https://mocksaml.com>`_ from Ory. For a full signup and login test, also check the
local mail capture service at `http://localhost:8887 <http://localhost:8887>`_ so you can complete account verification.
The test setup recognizes two mail domains and maps them to different user groups:

* ``example.com`` creates users in the ``student`` group.
* ``example.org`` creates users in the ``teacher`` group.

The allauth SAML guidelines highlight a few operational requirements that are easy to miss:

Most SAML identity providers require HTTPS, so plain :command:`runserver`-style testing is usually not
enough for realistic validation. Mock SAML is a practical exception and can work over HTTP, but
production-like tests should still run with TLS enabled.

When OpenBook is deployed behind a reverse proxy, configure Django to trust forwarded protocol and
host information by enabling ``USE_X_FORWARDED_HOST = True``,
``SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')``, and
``SECURE_SSL_REDIRECT = True``. The reverse proxy must also forward protocol metadata correctly so
that Django can reliably detect HTTPS requests.

Cookie settings should match the real deployment domain. Set ``CSRF_COOKIE_DOMAIN`` and
``SESSION_COOKIE_DOMAIN`` accordingly, and enable ``CSRF_COOKIE_SECURE`` and
``SESSION_COOKIE_SECURE`` to ensure cookies are only transmitted over HTTPS. During SAML testing,
run login flows in browser privacy mode, inspect the network exchange in developer tools, and use a
tracer such as SAML Tracer to verify the exchanged assertions and attribute mappings.
