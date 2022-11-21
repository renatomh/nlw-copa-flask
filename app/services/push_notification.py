# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:04:22 2022

@author: RenatoHenz
"""

# Module to get the environment variables
import os

# Modules for Firebase
from firebase_admin import messaging, credentials
import firebase_admin

# Getting the required variables
from config import BASE_DIR

# Firebase Cloud Messaging
if os.environ.get('PUSH_NOTIFICATION_DRIVER') == 'fcm':
    # Getting Firebase credentials
    creds = credentials.Certificate(BASE_DIR + os.sep + os.environ.get('FCM_CREDS_JSON_FILE'))
    
    # Initializing the Firebase app
    default_app = firebase_admin.initialize_app(creds)

    # Function to send a push notification for a specific token
    def send_message(token, title, body, data=None):
        # Creating the FCM message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            token=token
        )
        # Sending the defined message
        response = messaging.send(message)
        # Showing server response and returning to the user
        print(response)
        return response

    # Function to send a push notification for a set of tokens
    def send_multicast_message(tokens, title, body, data=None):
        # Checking if user has provided a lista of tokens
        try: assert isinstance(tokens, list)
        # If not, we'll inform about the error and return
        except Exception as e:
            print(e)
            return

        # Creating the FCM message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            tokens=tokens
        )
        # Sending the defined message
        response = messaging.send_multicast(message)
        # Showing server response and returning to the user
        print(response)
        return response

# If no driver was provided
else:
    # Function to send a push notification for a specific token
    def send_message(token, title, body, data=None):
        # Informing user about no driver provided
        print('No driver provided')
        return

    # Function to send a push notification for a set of tokens
    def send_multicast_message(tokens, title, body, data=None):
        # Informing user about no driver provided
        print('No driver provided')
        return
