# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:29:11 2021

@author: RenatoHenz
"""

# Importing config data
from config import PORT, HOST
# Importing the app
from app import app, socketio

# Defining which OS is being used
import platform

# For Windows
if platform.system() == 'Windows':
    # Serving the app on Windows
    if __name__ == "__main__":
        socketio.run(app, host=HOST, port=PORT)

# For Linux
if platform.system() == 'Linux':
    # Serving the app on Linux
    if __name__ == "__main__":
        socketio.run(app, host=HOST, port=PORT)
