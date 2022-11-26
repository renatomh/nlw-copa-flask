<h1 align="center"><img alt="NLW Copa Server" title="NLW Copa Server" src=".github/logo.svg" width="250" /></h1>

# NLW Copa Server

## 💡 Project's Idea

This project was developed during the RocketSeat's Next Level Week - Copa event. It aims to create a *backend* server application for providing world cup pools for friends which are loooking for placing their bets on the Fifa 2022 World Cup Games.

## 🔍 Features

* Users register/login;
* Available pools listing;
* New pools creation;
* Users count;
* Available games listing;
* New guesses creation;
* Available guesses listing;

## 💹 Extras

* New games creation;
* Pools ranking listing;
* Games results setting (with auto score updating for guesses and participants);

## 🛠 Technologies

During the development of this project, the following techologies were used:

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask-Babel](https://flask-babel.tkte.ch/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/index.html)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Gunicorn](https://gunicorn.org/)
- [Let's Encrypt](https://letsencrypt.org/pt-br/)

## 💻 Project Configuration

### First, create a new virtual environment on the root directory

```bash
$ python -m venv env
```

### Activate the created virtual environment

```bash
$ .\env\Scripts\activate # On Windows machines
$ source ./env/bin/activate # On MacOS/Unix machines
```

### Install the required packages/libs

```bash
(env) $ pip install -r requirements.txt
```

### Internationalization (i18n) and Localization (l10n)

In order to provide results according to the specified languages set in the request headers ([*Accept-Language*](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Headers/Accept-Language)), we make use of [Flask-Babel](https://flask-babel.tkte.ch/). Here are a few commands for its use:

```bash
(env) $ pybabel extract -F babel.cfg -k _l -o messages.pot . # Gets list of texts to be translated
(env) $ pybabel init -i messages.pot -d app/translations -l pt # Creates file (messages.po) with 'pt' translations (replace 'pt' with required language code)
(env) $ pybabel update -i messages.pot -d app/translations -l pt # Updates file (messages.po) with 'pt' translations (replace 'pt' with required language code)
(env) $ pybabel compile -d app/translations # Compiles the translation files
```

It's important to compile the translation files before running the application, should it provide the correct translations for the system users.

## 🌐 Setting up config files

Create an *.env* file on the root directory, with all needed variables, credentials and API keys, according to the sample provided (*.env.example*).

### Microsoft SQL Server

When using the Microsoft SQL Server, it is also required to [download and install the ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15). Otherwise, it won`t be possible to connect with the SQL server.

Also, in order to install *pyodbc* on Linux, it might be necessary to install *unixodbc-dev* with the command below:

```bash
$ sudo apt-get install unixodbc-dev
```

### MySQL Server

When using the Microsoft SQL Server, it is required to choose a default charset which won't conflict with some models fields data length. The 'utf8/utf8_general_ci' should work.

### Firebase Cloud Messaging

In order to be able to send *push notifications* to mobile applications, currently the [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging) solution it's being used. Aside from setting the *.env* file, you must also have your service account JSON credentials file present on the app's root folder.

### Time Zones

Since the application allows working with different time zones, it might be interesting to use the same time zone as the machine where the application is running when defining the *TZ* variable on the *.env* file, since internal database functions (which are used for creating columns like *created_at* and *updated_at*) usually make use of the system's time zone (when not set manually).

Also, on server's migration, the database backup could be coming from a machine with a different time zone definition. In this case, it might be necessary to convert the datetime records to the new machine time zone, or set the new machine time zone to the same as the previous machine.

## ⏯️ Running

To run the project in a development environment, execute the following command on the root directory, with the virtual environment activated.

```bash
(env) $ python run.py
```

In order to leave the virtual environment, you can simply execute the command below:

```bash
(env) $ deactivate
```

## 🔨 *Production* Server

In order to execute the project in a production server, you must make use of a *Web Server Gateway Interface* (WSGI), such as [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) for Linux or [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/) for Windows.

### 💻 Windows
In Windows, you could run the *wsgi.py* file, like so:

```bash
(env) $ python wsgi.py
```

After that, a Windows Task can be created to restart the application, activating the virtual environment and calling the script, whenever the machine is booted.

### ⌨ Linux
In Linux systems, you can use the following command to check if the server is working, changing the port number to the one you're using in the app:

```bash
(env) $ gunicorn --worker-class eventlet --bind 0.0.0.0:8080 wsgi:app --reload
```

The *nlw-copa.service* file must be updated and placed in the '/etc/systemd/system/' directory. After that, you should execute the following commands to enable and start the service:

```bash
$ sudo systemctl start nlw-copa
$ sudo systemctl enable nlw-copa
$ sudo systemctl status nlw-copa
```

In order to serve the application with Nginx, it can be configured like so (adjusting the paths, server name, etc.):

```
# Flask Server
server {
    listen 80;
    server_name nlw-copa.mhsw.com.br;

    location / {
        include proxy_params;
        proxy_pass http://localhost:8080;
        client_max_body_size 16M;
    }

    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://localhost:8080/socket.io;
    }
}
```

#### 📜 SSL/TLS

You can also add security with SSL/TLS layer used for HTTPS protocol. One option is to use the free *Let's Encrypt* certificates.

For this, you must [install the *Certbot*'s package](https://certbot.eff.org/instructions) and use its *plugin*, with the following commands (also, adjusting the srver name):

```bash
$ sudo apt install snapd # Installs snapd
$ sudo snap install core; sudo snap refresh core # Ensures snapd version is up to date
$ sudo snap install --classic certbot # Installs Certbot
$ sudo ln -s /snap/bin/certbot /usr/bin/certbot # Prepares the Certbot command
$ sudo certbot --nginx -d nlw-copa.mhsw.com.br
```

### Documentation:
* [Como servir os aplicativos Flask com o Gunicorn e o Nginx no Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04-pt)
* [Como servir aplicativos Flask com o uWSGI e o Nginx no Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04-pt)
* [How to host multiple flask apps under a single domain hosted on nginx?](https://stackoverflow.com/questions/34692600/how-to-host-multiple-flask-apps-under-a-single-domain-hosted-on-nginx)
* [Deploying Flask on Windows](https://towardsdatascience.com/deploying-flask-on-windows-b2839d8148fa)
* [Deploy de aplicativo Python / Flask no windows](https://www.tecnasistemas.com.br/hc/pt-br/articles/360041410791-Deploy-de-aplicativo-Python-Flask-no-windows)
* [How to serve static files in Flask](https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask)
* [Get list of all routes defined in the Flask app](https://stackoverflow.com/questions/13317536/get-list-of-all-routes-defined-in-the-flask-app)
* [Switching from SQLite to MySQL with Flask SQLAlchemy](https://stackoverflow.com/questions/27766794/switching-from-sqlite-to-mysql-with-flask-sqlalchemy)
* [Token-Based Authentication With Flask](https://realpython.com/token-based-authentication-with-flask/#user-status-route)
* [Define Relationships Between SQLAlchemy Data Models](https://hackersandslackers.com/sqlalchemy-data-models/)
* [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
* [Uploading Files](https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/)
* [Python - Flask - Working with middleware for specific route](https://www.youtube.com/watch?v=kJSl7pWeOfU)
* [Como Instalar o Python 3 e Configurar um Ambiente de Programação no Ubuntu 18.04 [Quickstart]](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-18-04-quickstart-pt)
* [What is the meaning of "Failed building wheel for X" in pip install?](https://stackoverflow.com/questions/53204916/what-is-the-meaning-of-failed-building-wheel-for-x-in-pip-install)
* [Install Certbot on ubuntu 20.04](https://askubuntu.com/questions/1278936/install-certbot-on-ubuntu-20-04)
* [The Flask Mega-Tutorial Part XIII: I18n and L10n](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n)
* [Flask Babel - 'translations/de/LC_MESSAGES/messages.po' is marked as fuzzy, skipping](https://stackoverflow.com/questions/12555692/flask-babel-translations-de-lc-messages-messages-po-is-marked-as-fuzzy-skip)
* [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
* [How to translate text with python](https://medium.com/analytics-vidhya/how-to-translate-text-with-python-9d203139dcf5)
* [deep-translator - PyPI](https://deep-translator.readthedocs.io/en/latest/)
* [How to Install FFmpeg on Windows, Mac, Linux Ubuntu and Debian](https://www.videoproc.com/resource/how-to-install-ffmpeg.htm)
* [Using PYTHONPATH](https://bic-berkeley.github.io/psych-214-fall-2016/using_pythonpath.html)
* [How do you set your pythonpath in an already-created virtualenv?](https://stackoverflow.com/questions/4757178/how-do-you-set-your-pythonpath-in-an-already-created-virtualenv)
* [cannot import local module inside virtual environment from subfolder](https://stackoverflow.com/questions/58642026/cannot-import-local-module-inside-virtual-environment-from-subfolder)
* [Socket.IO](https://socket.io/pt-br/)
* [Gunicorn ImportError: cannot import name 'ALREADY_HANDLED' from 'eventlet.wsgi' in docker](https://stackoverflow.com/questions/67409452/gunicorn-importerror-cannot-import-name-already-handled-from-eventlet-wsgi)
* [Error when running Flask application with web sockets and Gunicorn](https://stackoverflow.com/questions/56532961/error-when-running-flask-application-with-web-sockets-and-gunicorn)
* [eventlet worker: ALREADY_HANDLED -> WSGI_LOCAL #2581](https://github.com/benoitc/gunicorn/pull/2581)
* [polling-xhr.js:157 Error 502 Bad Gateway While trying to establish connection between the client and the server using SocketIO #1804](https://github.com/miguelgrinberg/Flask-SocketIO/discussions/1804)
* [Firebase Admin Python SDK](https://firebase.google.com/docs/reference/admin/python/)
* [Firebase cloud messaging and python 3](https://blog.iampato.me/firebase-cloud-messaging-and-python-3)

## 📄 License

This project is under the **MIT** license. For more information, access [LICENSE](./LICENSE).
