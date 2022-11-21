# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:29:11 2021

@author: RenatoHenz

Refs:
    * Flask Request Documentation: https://tedboy.github.io/flask/generated/generated/flask.Request.html
    * SQLAlchemy Operator Reference: https://docs.sqlalchemy.org/en/14/core/operators.html
    
"""

# Import flask dependencies
from flask import Blueprint, request, jsonify, g
from flask_babel import _

# Session maker to allow database communication
from app import AppSession

# Other dependencies
import requests
import json

# Middlewares
from app.middleware import ensure_authenticated

# Import module forms
from app.modules.users.forms import *

# Import module models
from app.modules.users.models import *

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/')
mod_user = Blueprint('users', __name__, url_prefix='/users')

# Route to count number of users
@mod_user.route('/count', methods=['GET'])
def count_users():
    if request.method == 'GET':
        try:
            count = User.query.count()
            return jsonify({"count": count})

        # If something goes wrong
        except Exception as e:
            return jsonify({"message": str(e)}), 500

# Route to get user's data
@mod_auth.route('/me', methods=['GET'])
@ensure_authenticated
def get_user_data():
    if request.method == 'GET':
        try:
            user = g.user
            return jsonify({"user": {"name": user.name, "avatarUrl": user.avatarUrl, "sub": user.id}})

        # If something goes wrong
        except Exception as e:
            return jsonify({"message": str(e)}), 500

# Route to register a new user or login an existing one
@mod_user.route('', methods=['POST'])
def sign_up_in():
    if request.method == 'POST':
        # Creating the session for database communication
        with AppSession() as session:
            # If data form is submitted
            form = SignUpinForm.from_json(request.json)

            # Validating provided data
            if form.validate():
                # Getting access token
                access_token = form.access_token.data

                # Trying to get user's data from google
                userResponse = requests.get(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={"Authorization": f"Bearer {access_token}"}
                    )

                # If there was an error on the response
                if not userResponse.ok:
                    return jsonify({"message": json.loads(userResponse.text)}), userResponse.status_code

                # Otherwise, we get the user's data
                userInfo = json.loads(userResponse.text)

                # Checking ff there's already a user with the specified ID
                user = User.query.filter(User.googleId == userInfo['id']).first()

                # If user is not registered yet, we'll create it
                if user == None:
                    user = User(
                        googleId=userInfo['id'],
                        name=userInfo['name'],
                        email=userInfo['email'],
                        avatarUrl=userInfo['picture'],
                        )
                    session.add(user)
                    # Flushing and comitting the changes
                    session.flush()
                    session.commit()

                # Generating user's token
                token = user.encode_auth_token(user.id)

                # Returning user's token
                return jsonify({"token": token})

            # If something goes wrong on data validation
            else:
                # Returning the data to the request
                return jsonify({"message": form.errors}), 400
