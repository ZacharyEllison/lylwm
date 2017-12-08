import csv
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps

"""This should be filled with magic numbers and helper functions"""


port = 31416
UPLOAD='/home/lylwm/lylwm/static/home/'
usrnm = 'username'
pswd = 'password'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'bmp'])
IMG_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp'])

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

"""Document should be
        string filename
        string filetype
        string file size
        string location
        string user who uploaded
        whether others can delete
"""
