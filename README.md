#Live Your Life With Me
Visit willyou.liveyourlifewith.me

##Introduction
Live Your Life With Me (lylwm) is a personal cloud storage solution. It's meant to be loaded onto a Raspberry Pi (any model) and attached to an open port on the users home network. The name comes from the URL Zachary purchased when creating this website, and could ultimately be any URL that the user wants to associate with the server. Because of the small nature of this, it's not meant to be extremely secure. Files uploaded will be uploaded to lylwm/static/home.

##Getting Started:
To get started with this application one needs only a computer with an internet connection. There are two dependencies: Flask and Pymongo.
###Database
This uses a NoSQL MongoDB database, that is presently setup to run off of a cloud database hosted at mlab. One can run this program with a locally hosted mongo database. The server would need MongoDB installed. To change it in application.py, switch line 18 from referencing mlab to read "client = MongoClient('localhost', <port>)" where port can be defined and referenced from helpers.py. In testing, the port I used was my daughter's birthday. In a command shell, prior to launching the site, one need only write "$ sudo mongod --ipv6 --journal --smallfiles --port 31416" where 31416 could be any port the user wishes or omitted for the port to be the default 27017.
###Flask
This uses a normal build of flask. Flask session had to be installed separately on the testing machine and the present host, PythonAnywhere. As it is configured, debug is on as this is still in beta stages. That can be changed on line 34 of application.py. If there are issues running "flask run" try running "$ export FLASK_APP=application.py" or whatever you might rename the main application to, and trying again.
###Website Use
The website is simple. Everything is behind a login wall, so first register an account with a password longer than 8 characters. After logging in, in the adventures dropdown menu, go to add more. This will bring you to the upload page where you can upload images and files, choose tags from previously uploaded files, add new tags separated by a space, and give permission to others to delete it. If permission is not given, the Admin will still be able to delete it. After uploading files, you can go to adventures dropdown and to explore. There you can explore the files uploaded, delete them from the hard drive, or download them to yours.