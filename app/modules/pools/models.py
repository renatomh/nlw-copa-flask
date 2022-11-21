# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 16:31:11 2022

@author: RenatoHenz
"""

# Getting config data
from config import tz

# Import the database object (db) from the main application module
from app import db

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
    id = db.Column(db.String(32), primary_key=True, default=cuid.cuid())
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                        onupdate=db.func.current_timestamp())

# Define a Pool model using Base columns
class Pool(Base):
    __tablename__ = 'pool'

    title = db.Column(db.String(256), nullable=False)
    code = db.Column(db.String(6), nullable=False, unique=True)
    ownerId = db.Column(db.String(32), db.ForeignKey('user.id'), nullable=True)

    # Relationships
    participants = db.relationship('Participant', lazy="select", backref='pool')

    # New instance instantiation procedure
    def __init__(self, title, code, ownerId=None):
        self.title = title
        self.code = code
        self.ownerId = ownerId

    def __repr__(self):
        return '<Pool %r>' % (self.id)

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

# Define a Participant model using Base columns
class Participant(Base):
    __tablename__ = 'participant'

    userId = db.Column(db.String(32), db.ForeignKey('user.id'), nullable=False)
    poolId = db.Column(db.String(32), db.ForeignKey('pool.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    guesses = db.relationship('Guess', lazy="select", backref='participant')

    # New instance instantiation procedure
    def __init__(self, userId, poolId, score=0):
        self.userId = userId
        self.poolId = poolId
        self.score = score

    def __repr__(self):
        return '<Participant %r>' % (self.id)

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

# Define a Game model using Base columns
class Game(Base):
    __tablename__ = 'game'

    date = db.Column(db.DateTime, nullable=False)
    firstTeamCountryCode = db.Column(db.String(128), nullable=False)
    secondTeamCountryCode = db.Column(db.String(128), nullable=False)
    firstTeamPoints = db.Column(db.Integer, nullable=True)
    secondTeamPoints = db.Column(db.Integer, nullable=True)

    # Relationships
    guesses = db.relationship('Guess', lazy="select", backref='game')

    # New instance instantiation procedure
    def __init__(self, date, firstTeamCountryCode, secondTeamCountryCode, firstTeamPoints=None, secondTeamPoints=None):
        self.date = date
        self.firstTeamCountryCode = firstTeamCountryCode
        self.secondTeamCountryCode = secondTeamCountryCode
        self.firstTeamPoints = firstTeamPoints
        self.secondTeamPoints = secondTeamPoints

    def __repr__(self):
        return '<Game %r>' % (self.id)

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

# Define a Guess model using Base columns
class Guess(Base):
    __tablename__ = 'guess'

    firstTeamPoints = db.Column(db.Integer, nullable=False)
    secondTeamPoints = db.Column(db.Integer, nullable=False)
    gameId = db.Column(db.String(32), db.ForeignKey('game.id'), nullable=False)
    participantId = db.Column(db.String(32), db.ForeignKey('participant.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)

    # New instance instantiation procedure
    def __init__(self, firstTeamPoints, secondTeamPoints, gameId, participantId, score=0):
        self.firstTeamPoints = firstTeamPoints
        self.secondTeamPoints = secondTeamPoints
        self.gameId = gameId
        self.participantId = participantId
        self.score = score

    def __repr__(self):
        return '<Guess %r>' % (self.id)

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
