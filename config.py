# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Statement for enabling the development environment
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Setting up the '.env' file with environment variables
from dotenv import load_dotenv
load_dotenv('.env')

# Defining the default timezone for the application
import pytz
# If environment timezone name changes, all datetimes on database might have to be corrected
tz = pytz.timezone(os.getenv('TZ', 'UTC'))

# This module is required for usernames and passwords with special characters
from urllib.parse import quote
# Define the database
if os.environ.get('SQL_DRIVER') == 'sqlite':
    # 'check_same_thread=False' arg is required when using SQLlite3 to avoid 'ProgrammingError'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(BASE_DIR, os.environ.get('SQL_DB') + '.db') + '?check_same_thread=False'
elif os.environ.get('SQL_DRIVER') == 'mysql':
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQL_DRIVER') + '+pymysql://' + quote(os.environ.get('SQL_USER')) + ':' + quote(os.environ.get(
        'SQL_PASS')) + '@' + os.environ.get('SQL_HOST') + ':' + os.environ.get('SQL_PORT') + '/' + os.environ.get('SQL_DB')
DATABASE_CONNECT_OPTIONS = {}
# Option to try avoiding problemas of connection with SQL server being lost
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size' : 100, 'pool_recycle' : 280, 'pool_pre_ping': True}

# Available languages for internationalization/localization (i18n, l10n)
LANGUAGES = {
    'en': 'English',
    'pt': 'Portuguese',
    'es': 'Spanish'
}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection against *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = os.environ.get('APP_SECRET')

# Secret key for signing cookies
SECRET_KEY = os.environ.get('APP_SECRET')

# Defining serve port number and host
PORT = os.environ.get('PORT')
HOST = os.environ.get('HOST')
