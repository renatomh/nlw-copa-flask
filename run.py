# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:29:11 2021

@author: RenatoHenz
"""

# Importing config data
from config import PORT, HOST

# Running the server
from app import app, socketio
socketio.run(app, host=HOST, port=PORT, debug=True)
