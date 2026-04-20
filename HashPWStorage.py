# SQLAlchemy code adapted from GeeksforGeeks 
# https://www.geeksforgeeks.org/python/connect-flask-to-a-database-with-flask-sqlalchemy/

from flask import Flask, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import hashlib
import string
import random

# Flask setup
app = Flask(__name__)
app.debug = True
# SQL setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning
db = SQLAlchemy(app)
# Migrate setup
migrate = Migrate(app, db)

# db Model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    pwh = db.Column(db.String(20), nullable=False)
    hashid = db.Column(db.String(20, nullable=False))

    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"ID: {self.hashid}, Name : {self.username}, Password Hash: {self.pwh}"

# Function to render index page
@app.route('/')
def index():
    profiles = Profile.query.all()
    return render_template('index.html', profiles=profiles)

# Function to render add profile page
@app.route('/add_data')
def add_data():
    return render_template('add_profile.html')

# Function to render login page and check passwords
@app.route('/login', methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        # Get username and password from form
        username = request.form.get("username")
        password = request.form.get("password")
        # Create hash object using password from form
        pwh = hashlib.sha256()
        pwh.update(password.encode("utf-8"))
        pwh_hash = pwh.hexdigest()
        # Find actual password using username from form
        user = db.one_or_404(db.select(Profile).filter_by(username=username))
        # Check password
        if user.pwh == pwh_hash:
            return redirect('/') # TODO: Create a page to navigate to after logging in
        else:
            msg = "Login unsuccessful. Incorrect username/password!"
    return render_template('login.html', msg=msg)

# Function to add profiles
@app.route('/add', methods=["POST"])
def profile():
    # Get username and password from form
    username = request.form.get("username")
    pw = request.form.get("password")
    # Create hash object using password from form
    pwh = hashlib.sha256()
    pwh.update(pw.encode("utf-8"))
    pwh_hash = pwh.hexdigest()
    # Convert digest into string
    pwh_str = f"{pwh_hash}"
    
    ##
    # Source - https://stackoverflow.com/a/23728630
    # Posted by Randy Marsh, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-04-17, License - CC BY-SA 4.0  
    ##
    # Create salt for id hash
    salt = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(6))
    salted_user = username + salt
    # Create hash object using username and salt
    unh = hashlib.md5()
    unh.update(salted_user.encode("utf-8"))
    unh_hash = unh.hexdigest()
    # Convert digest into string
    hashid = f"{unh_hash}"

    if username != '' and pw != '':
        p = Profile(username=username, pwh=pwh_str, hashid=hashid)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

# Function to delete table entries
@app.route('/delete/<int:id>')
def erase(id): 
    data = Profile.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():  # Needed for DB operations outside a request
        db.create_all()      # Creates the database and tables
    app.run(debug=True)