import csv
import os
import urllib.request
from pymongo import MongoClient
from flask import redirect, render_template, request, session
from functools import wraps

"""This should be filled with magic numbers and helper functions"""

# Setup for pymongo with port in helpers.py and the databases I'll use
DB_USER = "admin"
DB_PASS = "secretpassword1"
client = MongoClient("ds044577.mlab.com", 44577)
home_db = client['home']
home_db.authenticate(DB_USER, DB_PASS)

users = home_db.users
items = home_db.items
record = home_db.record

port = 31416
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD='static/home/'
usrnm = 'username'
pswd = 'password'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'bmp', 'JPG', 'JPEG'])
IMG_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'JPG', 'JPEG'])

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
def check(filename):
    '''Pass in secure_filename, check for dubplicates'''
    # Parse the string
    name_split = filename.split(".")
    first = list(name_split[0])
    # Find how many in DB
    if items.find_one({'name': filename}):
        how_many = len(items.find_one({'name': filename})) % 8

        # If you find a file with this name already
        if how_many > 0:
            first.extend('_' + str(how_many))

    # Add back the extension of the file
    first.append('.' + name_split[1])

    return ''.join(first)

# Thanks to Fred Cirera: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
