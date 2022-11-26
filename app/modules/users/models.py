# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 16:31:11 2022

@author: RenatoHenz
"""

# Import flask dependencies
import os

# Getting config data
from config import tz

# Import the database object (db) from the main application module
from app import db

# JWT for token generation
import jwt

# Library to deal with dates, UTC, etc.
from datetime import datetime, timedelta

# Other dependencies
import cuid

# Function to format an object (like datetime/date) to a string
def default_object_string(object):
    if str(type(object)) == "<class 'datetime.datetime'>":
        return object.isoformat()
    elif str(type(object)) == "<class 'datetime.date'>":
        return object.strftime("%Y-%m-%d")
    return object

# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    # Defining base columns
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                        onupdate=db.func.current_timestamp())

# Define a User model using Base columns
class User(Base):
    __tablename__ = 'user'

    id = db.Column(db.String(32), primary_key=True)

    # User Name
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    googleId = db.Column(db.String(512), nullable=True, unique=True)
    avatarUrl = db.Column(db.String(1024), nullable=True)
    fcmToken = db.Column(db.String(512), nullable=True)

    # Relationships
    participatingAt = db.relationship('Participant', lazy="select", backref='user')
    ownPools = db.relationship('Pool', lazy="select", backref='owner')

    # New instance instantiation procedure
    def __init__(self, name, email, googleId=None, avatarUrl=None, fcmToken=None):
        self.id = cuid.cuid()
        self.name = name
        self.email = email
        self.googleId = googleId
        self.avatarUrl = avatarUrl
        self.fcmToken = fcmToken

    def __repr__(self):
        return '<User %r>' % (self.id)

    # Returning data as dict
    def as_dict(self, timezone=tz):
        # We also remove the password
        data = {c.name: default_object_string(getattr(self, c.name))
                for c in self.__table__.columns
                if c.name != "hashpass"}
        # Adding the related tables
        for c in self.__dict__:
            if 'app' in str(type(self.__dict__[c])):
                data[c] = self.__dict__[c].as_dict(timezone)
            # For many-to-many relationships
            if 'InstrumentedList' in str(type(self.__dict__[c])):
                # Adding the itens IDs
                data[c+'_ids'] = [i.id for i in self.__dict__[c]]
        return data

    # Enconding the authentication token
    def encode_auth_token(self, id):
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=7, hours=2, minutes=30, seconds=0),
                'iat': datetime.utcnow(),
                'sub': id
            }
            return jwt.encode(
                payload,
                os.environ.get('APP_SECRET'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    # Decoding the authentication JWT
    @staticmethod
    def decode_auth_token(token):
        try:
            # For newer versions of PyJWT (>= 2.0.0), we must add the 'algorithms' arg
            payload = jwt.decode(token, os.environ.get('APP_SECRET'), algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Token expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
