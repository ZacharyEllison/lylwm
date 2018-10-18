from flask import Flask, flash, redirect, render_template, current_app
from flask import request, session, send_from_directory, url_for
from flask_session import Session
from tempfile import mkdtemp
from bson.objectid import ObjectId
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from lylwm_ui.helpers import UPLOAD, usrnm, pswd, ALLOWED_EXTENSIONS, login_required, IMG_EXTENSIONS, check, basedir, sizeof_fmt
from datetime import datetime
import os

from lylwm_ui import settings, db


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config['DEBUG'] = settings.DEBUG
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# have a check for allowed files (from Flask API)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Index is a simple page need only render
@app.route("/")
def index():
    """Main Page"""
    return render_template("index.html")


# Explore is mostly done in Jinja, iterating over the list passed in
@app.route("/explore")
@login_required
def explore():
    """Display files based on page"""
    list_items = items.find({})
    return render_template("explore.html", items=list_items, img_list=IMG_EXTENSIONS)


@app.route('/viewer/<file_name>')
@login_required
def view(file_name):
    """Renders a view of a single image"""
    file = items.find_one({'name': file_name})
    if file == None:
        flash("File not found")
        return redirect(request.url)
    return render_template('viewer.html', file=file)


@app.route("/download/<string:fileid>")
@login_required
def download(fileid):
    """Give download and redirect back to explore, the big thing here is the html"""

    file_give = items.find_one({'_id': ObjectId(fileid)})
    # Check for the file to exist
    if items.find_one({'_id': ObjectId(fileid)}):

        # Record the action
        record.insert_one({
            'user': session["user_id"],
            'action': 'Download',
            'file': file_give['name'],
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        # All is well and working
        uploads = os.path.join(current_app.root_path, UPLOAD)
        return send_from_directory(directory=uploads, filename=file_give['name'], as_attachment=True)

    else:
        flash("File not found")
        return redirect('/explore')


@app.route("/delete/<string:file_id>")
@login_required
def delete(file_id):
    """Deletes a file given by its id"""

    # Check if the file exists
    if items.find_one({'_id': ObjectId(file_id)}) is not None:

        # Access as a local variable
        del_item = items.find_one({'_id': ObjectId(file_id)})
        # check permission
        if del_item['permission'] == "Yes" or users.find_one({'_id': ObjectId(session["user_id"])})['username'] == 'admin':
            # Delete from database then system
            items.delete_one({'_id': ObjectId(file_id)})
            os.remove(os.path.join(os.path.join(current_app.root_path, UPLOAD), del_item['name']))

            # Record the action
            record.insert_one({
                'user': session["user_id"],
                "action": "Delete",
                "file": del_item['name'],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            flash("successfully deleted file")
            return redirect("/explore")
        else:
            flash("You don't have permission for that")
            return redirect("/explore")
    else:
        flash("File not found")
        return redirect("/explore")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Uploads a file to the db and home folder"""
    tags=[]

    if items.distinct( "tags" ):
        tags = items.distinct( "tags" )

    if request.method == 'POST':
        # check if the post request has the file
        if 'file' not in request.files:
            flash('No file')
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # make sure we deal only in secure names
            name = check(secure_filename(file.filename))
            # Save the picture in the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], name))

            # track the checkbox
            if request.form.getlist("permission"):
                perm_tf = 'Yes'
            else:
                perm_tf = 'No'

            # I want to track the filename, size, type, date added, user who added, tags, permissions,
            items.insert_one({
                "name": name,
                "type": file.filename.split(".")[1],
                "size": sizeof_fmt(os.stat(os.path.join(UPLOAD, name)).st_size),
                "location": os.path.join(UPLOAD, name),
                "owner": users.find_one({'_id': ObjectId(session["user_id"])})['username'],
                "permission": perm_tf,
                "tags": request.form.get("new_tag").split(", "),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            # Let the record track uploads and downloads
            record.insert_one({
                "user": session["user_id"],
                "action": 'Upload',
                "file": name,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            # All worked well
            flash("File uploaded successfully")
            return redirect("/")

        # It's not an allowed file
        else:
            flash("Unsupported file type")
            return redirect(url_for("upload"))
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
            flash("username taken")
            return render_template("register.html")
        # Make an object that represents the new user to be inserted
        new_user = {'username': usr, 'password': generate_password_hash(pswd_get)}

        # This command inserts the new user dict object and collects the unique id
        new_id = users.insert_one(new_user).inserted_id

        # Redirect user to home page when correct and done
        flash("Account successfully created")
        # Remember which user has logged in
        session["user_id"] = str(new_id)
        return redirect(url_for('index'))

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
    return redirect(url_for('index'))


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
            return redirect(request.url)
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
        return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", pass_wrong = False)


def create(debug=False):
    app = Flask(__name__)
    app.debug = debug

    static_path = os.path.join(app.root_path, 'static')
    favicon_path = os.path.join(static_path, 'favicon')

    @app.errorhandler(400) # bad request
    @app.errorhandler(400) # unauthorized
    @app.errorhandler(403) # forbidden
    @app.errorhandler(404) # not found
    @app.errorhandler(500) # server error
    @app.errorhandler(503) # service unavailable
    @json
    def err(err):
        if hasattr(err, 'code') and err.code == 404:
            err.description = 'not found'
        return {'error': err.description if hasattr(err, 'description') else 'unclear error'}, err.code if hasattr(err, 'code') else 500

    @app.route('/favicon-16.png')
    @app.route('/favicon-32.png')
    @app.route('/favicon-96.png')
    def favicon():
        size = ''.join([s for s in request.path if s.isdigit()])
        return send_from_directory(favicon_path, 'favicon-{}.png'.format(size))

    return app


app = create(
    debug=settings.DEBUG
)


def run():
    logger.info(f'starting app.. port={settings.PORT} debug={settings.DEBUG}')
    app.run(host='0.0.0.0', port=settings.PORT)