import argparse
import base64
import os
import shutil
import time
from datetime import datetime
from io import BytesIO

import eventlet
import eventlet.wsgi

import socketio

from flask import Flask

start_time = time.time()

sio = socketio.Server()
app = Flask(__name__)
model = None
prev_image_array = None

num_user = 0
username = {}


@sio.on('new message')
def new_message(sid, msg):
    global num_user, username
    if msg:
        print(username[sid], ': ', msg)
        sio.emit('new message', data={'message': msg, 'username': username[sid]}, skip_sid=sid)
        print(time.time())

    else:
        # NOTE: DON'T EDIT THIS.
        sio.emit('new message', data={}, skip_sid=True)


@sio.on('typing')
def typing(sid):
    global username
    sio.emit('typing', data={'username': username[sid]}, skip_sid=sid)


@sio.on('stop typing')
def stop_typing(sid):
    sio.emit('stop typing')


@sio.on('add user')
def add_user(sid, nickname):
    global num_user, username
    username[sid] = nickname
    print('Add user: ', nickname)
    sio.emit('user joined', data={'username': username[sid], 'numUsers': num_user}, skip_sid=sid)


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    global num_user
    num_user += 1
    a = int(num_user)
    sio.emit('login', data={'numUsers': a}, room=sid)


@sio.on('disconnect')
def disconnect(sid):
    global num_user, username
    num_user -= 1
    sio.emit('user left', data={'username': username[sid], 'numUsers': num_user})
    del username[sid]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple chat server')

    args = parser.parse_args()

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)
