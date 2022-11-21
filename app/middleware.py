# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:29:11 2021

@author: RenatoHenz
"""

# Functools module
from functools import wraps

# Required modules
from flask import request, g, jsonify
from flask_babel import _

# Import module models
from app.modules.users.models import *

# Middleware to get user data and check if it is authenticated
def ensure_authenticated(func):
    @wraps(func)
    def auth_function(*args, **kwargs):
        # If an auth header was provided
        try:
            # Getting user ID by token
            token = request.headers['Authorization'].split("Bearer ")[1]
            res = User.decode_auth_token(token)
            # If token is not valid
            if type(res) is not str:
                return jsonify({"message": _("Authentication failed. Please login to access the resource.")}), 401
            # Searching user by ID
            user = User.query.filter_by(id=res).first()
            # If no user is found
            if user is None:
                return jsonify({"message": _("Authentication failed. Please login to access the resource.")}), 401
            # If user is found
            g.user = user

        # Otherwise
        except Exception as e:
            return jsonify({"message": (_("Authentication failed. Please login to access the resource."), str(e))}), 401
        # Continue the execution
        return func(*args, **kwargs)

    return auth_function
