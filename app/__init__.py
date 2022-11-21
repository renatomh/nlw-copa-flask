# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 16:35:11 2022

@author: RenatoHenz

Refs:
    * Flask Limiter Documentation: https://flask-limiter.readthedocs.io/en/stable/

"""

# Import flask and template operators
from flask import Flask, jsonify
from flask.globals import request

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Import Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# Setting up limiter to avoid DOS attacks
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10/second"]
)

# Import CORS
from flask_cors import CORS
# Allowing access through sites (such as when using ReactJS)
CORS(app)

# Import Flask-Babel
from flask_babel import Babel, _
# Adding internationalization and location to app
babel = Babel(app)
# Selecting language according to Accept-Language header from the incoming request
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

# Import Socket.IO
from flask_socketio import SocketIO, emit
# Creating the Socket.IO server
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Defining Socket.IO listeners
# Event listener when client connects to the server
@socketio.on("connect")
def connected():
    print(f"New client has connected (SID: {request.sid})")

# Event listener for when client sends generic data via 'event'
@socketio.on('event')
def handle_message(data):
    print(f"Data from client (SID: {request.sid}):", str(data))
    #emit("event", {'data': data, 'id': request.sid}, broadcast=True)

# Event listener when client disconnects from the server
@socketio.on("disconnect")
def disconnected():
    print(f"Client has disconnected (SID: {request.sid})")

# Middlewares
from app.middleware import ensure_authenticated

# Setting up sample Socket.IO messages sending route
@app.route('/send_socketio_message', methods=['POST'])
@ensure_authenticated
def send_socketio_message():
    # For POST method
    if request.method == 'POST':
        # Getting request data as a dict
        data = request.json

        # Creating a list with possible errors to be returned to the client
        error_messages = []
        # Checking if the event name was provided
        if 'event' not in data.keys() or not data['event']:
            error_messages.append(_("You must provide the 'event' name."))
        # Checking if the broadcast flag was provided
        if 'should_broadcast' not in data.keys() or data['should_broadcast'] not in [True, False]:
            error_messages.append(_("You must inform if message should be broadcast "
                                        "('should_broadcast' flag as 'true' or 'false')."))
        # When not broadcasting, the session ID must be informed
        if 'should_broadcast' in data.keys() and not data['should_broadcast'] and ('sid' not in data.keys() or not data['sid']):
            error_messages.append(_("You must inform the session ID ('sid') when not "
                                        "broadcasting."))
        # Checking if the message content was provided
        if 'message' not in data.keys() or not data['message']:
            error_messages.append(_("You must provide the message content as 'json' "
                                        "to be sent."))
        # If there were errors on the request
        if len(error_messages) > 0:
            return jsonify({"data": [],
                            "meta": {"success": False,
                                     "errors": error_messages}}), 400

        # If everything is ok, we emit the message
        # If it's a broadcast
        if data['should_broadcast']: socketio.emit(data['event'], data['message'], broadcast=True)
        # If it's a message for a specific client
        else: socketio.emit(data['event'], data['message'], to=data['sid'])

        # Informing user about success
        return jsonify({"data": {"message": _("Message sent successfully")},
                        "meta": {"success": True}})

# Import services
from app.services.push_notification import send_message, send_multicast_message

# Setting up sample push notification message sending route
@app.route('/send_push_notification_message', methods=['POST'])
@ensure_authenticated
def send_push_notification_message():
    # For POST method
    if request.method == 'POST':
        # Getting request data as a dict
        data = request.json

        # Creating a list with possible errors to be returned to the client
        error_messages = []
        # Checking if the notification title was provided
        if 'title' not in data.keys() or not data['title']:
            error_messages.append(_("You must provide the notification 'title'."))
        # Checking if the notification body was provided
        if 'body' not in data.keys() or not data['body']:
            error_messages.append(_("You must provide the notification 'body'."))
        # Checking if the multicast flag was provided
        if 'should_multicast' not in data.keys() or data['should_multicast'] not in [True, False]:
            error_messages.append(_("You must inform if message should be multicast "
                                        "('should_multicast' flag as 'true' or 'false')."))
        # When not multicasting, one token must be provided
        if 'should_multicast' in data.keys() and not data['should_multicast'] and ('token' not in data.keys() or not data['token'] or \
            type(data['token']) != str):
            error_messages.append(_("You must inform one token ('token') when not "
                                        "multicasting."))
        # When multicasting, a list of tokens must be provided
        if 'should_multicast' in data.keys() and data['should_multicast'] and ('tokens' not in data.keys() or not data['tokens'] or \
            type(data['tokens']) != list):
            error_messages.append(_("You must inform a list of tokens ('tokens') when "
                                        "multicasting."))
        # If there were errors on the request
        if len(error_messages) > 0:
            return jsonify({"data": [],
                            "meta": {"success": False,
                                     "errors": error_messages}}), 400

        # If everything is ok, we send the push notification message
        try:
            # If it's a multicast
            if data['should_multicast']: send_multicast_message(data['tokens'], data['title'], data['body'])
            # If it's a message for a specific client
            else: send_message(data['token'], data['title'], data['body'])

            # Informing user about success
            return jsonify({"data": {"message": _("Message sent successfully")},
                            "meta": {"success": True}})
        # If an error occurs
        except Exception as e:
            return jsonify({"data": [],
                            "meta": {"success": False,
                                     "errors": str(e)}}), 500

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"data": [],
            "meta": {"message": _("Resource not found.")}}), 404
@app.errorhandler(413)
def ratelimit_handler(e):
    return jsonify({"data": [],
            "meta": {"message": (_('Content too large'), e.description)}}), 413
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"data": [],
            "meta": {"message": (_('Ratelimit exceeded'), f"{e.description}.")}}), 429

# Engine and Session for executing queries with ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from config import SQLALCHEMY_DATABASE_URI, DATABASE_CONNECT_OPTIONS
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True,
                        future=True, connect_args=DATABASE_CONNECT_OPTIONS)
# Defining a sessionmaker to use on modules routes
AppSession = sessionmaker(engine)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.modules.users.controllers import *
from app.modules.pools.controllers import *

# Register blueprint(s)
# Users modules
app.register_blueprint(mod_auth)
app.register_blueprint(mod_user)
# Pools modules
app.register_blueprint(mod_pool)
app.register_blueprint(mod_guess)
app.register_blueprint(mod_game)

# Build the database:
# This will create the database file using SQLAlchemy or the selected SQL database/driver
db.create_all()
