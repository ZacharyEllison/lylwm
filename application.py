from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from helpers import port, UPLOAD, usrnm, pswd
import pymongo
from datetime import datetime
import os

# Setup for pymongo with port in helpers.py and the databases I'll use
client = MongoClient('localhost', port)
home_db = client['home']
users = home_db.users
items = home_db.items

print("starting server")
app = Flask(__name__)
app.secret_key="adventureisoutthere"
# to make sure of the new app instance

now = datetime.now()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Main Page"""
    return render_template("index.html")


@app.route("/adventures/today")
def today():
    """This Page is meant to expand with time, for now it will be a way to look at what was uploaded or downloaded today by whom"""
    flash("TODO")
    return redirect("/")



@app.route("/adventures/explore.pg<pg_number>")
def explore(pg_number):
    """Display files based on page"""
    flash("TODO")
    return redirect("/")


@app.route("/adventures/download.<item_id>")
def download(item_id):
    """Give download and redirect back to explore, the big thing here is the html"""
    flash("TODO")
    return redirect("/")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Uploads a file to the db and home folder"""

    tags = items.distinct( "tags" )

    # Flask documentation shows uploads are the following
    if request.method == 'POST':
        file = request.files['file']
        # I will add to the database here
        # I want to track the filename, size, type, date added, user who added, tags, permissions,
        file.save(os.path.join(UPLOAD, secure_filename(file.filename)))
        """TODO"""
        flash("File uploaded successfully")
        return redirect("/")
    else:
        return render_template("upload.html", tags=tags)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    usrtkn = False

    # Forget any user_id from Session
    session.clear()

    # User reached the route via POST (submitting a form)
    if request.method == "POST":

        # JS checks for pass and user so we'll deal with db
        usr = request.form.get("username")
        pswd_get = request.form.get("password")

        # If the username exists in the db
        if users.find_one({usrnm: usr}):
            # Attempt to limit the steps the user takes with a flash and redirect back, so no error page
            return render_template("register.html", usrtkn=True)

        # Make an object that represents the new user to be inserted
        new_user = {'username': usr, 'password': generate_password_hash(pswd_get)}

        # This command inserts the new user dict object and collects the unique id
        new_id = users.insert_one(new_user).inserted_id

        # Redirect user to home page when correct and done
        flash("Account successfully created")
        # Remember which user has logged in
        session["user_id"] = str(new_id)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", usrtkn=False)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logout successful")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # JS takes care of text entry so collect the user and pass
        usr = request.form.get('username')
        psw = request.form.get('password')
        print(usr + " " + psw)
        # check the password against database
        if not users.find_one({'username': usr}):
            flash("user not found")
            return redirect("/")
        print(users.find_one({'username': usr}))
        check_usr = users.find_one({'username': usr})

        # I'm raising the exception that check_usr is non subscriptable but it is in my tests

        # If the password is wrong reload the page with the pass_wrong banner and try again
        if not check_password_hash(check_usr[pswd], psw):
            return render_template("login.html", pass_wrong = True)

        # Else it's correct
        session["user_id"] = str(check_usr['_id'])

        # Redirect user to home page
        flash("Successfully logged in")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", pass_wrong = False)

