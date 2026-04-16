# SQLAlchemy code adapted from GeeksforGeeks 
# https://www.geeksforgeeks.org/python/connect-flask-to-a-database-with-flask-sqlalchemy/

from flask import Flask, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import hashlib

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    pwh = db.Column(db.String(20), nullable=False)

    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"Name : {self.name}, Password Hash: {self.pwh}"

# function to render index page
@app.route('/')
def index():
    profiles = Profile.query.all()
    return render_template('index.html', profiles=profiles)

# function to render add profile page
@app.route('/add_data')
def add_data():
    return render_template('add_profile.html')

# function to render login page and check passwords
@app.route('/login', methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        pwh = hashlib.sha256()
        pwh.update(password.encode("utf-8"))
        pwh_hash = pwh.hexdigest()
        user = db.one_or_404(db.select(Profile).filter_by(name=username))
        if user.pwh == pwh_hash:
            return redirect('/') # TODO: Create a page to navigate to after logging in
        else:
            msg = "Login unsuccessful. Incorrect username/password!"
    return render_template('login.html', msg=msg)

# function to add profiles
@app.route('/add', methods=["POST"])
def profile():
    username = request.form.get("username")
    pw = request.form.get("password")
    pwh = hashlib.sha256()
    pwh.update(pw.encode("utf-8"))
    pwh_hash = pwh.hexdigest()
    pwh_str = f"{pwh_hash}"

    if username != '' and pw != '':
        p = Profile(name=username, pwh=pwh_str)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

# function to delete table entries
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