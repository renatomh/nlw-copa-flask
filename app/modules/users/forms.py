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
from wtforms import TextField

# Import Form validators
from wtforms.validators import Required

# Initiating JSON for forms
wtforms_json.init()

# Define the sign up/in form (WTForms)
class SignUpinForm(Form):
    access_token = TextField('Access Token', [
        Required(message='You must provide the access token.')
    ])
