from flask import Flask, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy

import hashlib

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning

db = SQLAlchemy(app)

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

@app.route('/add_data')
def add_data():
    return render_template('add_profile.html')

# function to add profiles
@app.route('/add', methods=["POST"])
def profile():
    name = request.form.get("name")
    pw = request.form.get("password")
    pwh = hashlib.sha256()
    pwh.update(pw)
    pwh.hexdigest

    if name != '' and pw != '':
        p = Profile(name=name, pwh=pwh)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

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