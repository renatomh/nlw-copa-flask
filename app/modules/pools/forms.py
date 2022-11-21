# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:29:11 2021

@author: RenatoHenz
"""

# Import Form
from wtforms import Form

# Import JSON extension for forms
import wtforms_json

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, IntegerField, DateTimeField

# Import Form validators
from wtforms.validators import Required, NumberRange, InputRequired

# Initiating JSON for forms
wtforms_json.init()

# Define the create pool form (WTForms)
class CreatePoolForm(Form):
    title = TextField('Title', [
        Required(message='You must provide the title.')
    ])

# Define the join pool form (WTForms)
class JoinPoolForm(Form):
    code = TextField('Code', [
        Required(message='You must provide the code.')
    ])

# Define the create guess form (WTForms)
class CreateGuessForm(Form):
    firstTeamPoints = IntegerField('First Team Points', [
        # InputRequired(message='You must provide the first team points.'),
        NumberRange(min=0, max=99)
    ])
    secondTeamPoints = IntegerField('Second Team Points', [
        # InputRequired(message='You must provide the second team points.'),
        NumberRange(min=0, max=99)
    ])

# Define the create game form (WTForms)
class CreateGameForm(Form):
    date = DateTimeField(
        'Date', 
        format='%Y-%m-%dT%H:%M:%S%z',
        validators=[
            Required("You must rovide the game's date")
        ]
    )
    firstTeamCountryCode = TextField('First Team Country Code', [
        Required(message='You must provide the first team country code.')
    ])
    secondTeamCountryCode = TextField('Second Team Country Code', [
        Required(message='You must provide the second team country code.')
    ])

# Define the set game result form (WTForms)
class SetGamResultForm(Form):
    firstTeamPoints = IntegerField('First Team Points', [
        # InputRequired(message='You must provide the first team points.'),
        NumberRange(min=0, max=99)
    ])
    secondTeamPoints = IntegerField('Second Team Points', [
        # InputRequired(message='You must provide the second team points.'),
        NumberRange(min=0, max=99)
    ])
