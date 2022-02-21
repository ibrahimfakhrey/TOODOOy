from flask import Flask, render_template, redirect, url_for, flash, abort, request


from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

import sqlite3
import os



app = Flask(__name__)



app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# db.create_all()

@app.route('/')
def start():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        login_user(new_user)
        return render_template("todo.html")

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Email exists and password correct
        else:
            login_user(user)
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT *  FROM User WHERE email=email")
            print(c.fetchone())


            return render_template("todo.html")

    return render_template("login.html")
todo=[]
@app.route('/submit', methods=['POST'])
def submit_textarea():
    # store the given text in a variable
    text = request.form.get("text")
    todo.append(text)
    #
    # # split the text to get each line in a list
    # text2 = text.split('\n')
    #
    # # change the text (add 'Hi' to each new line)
    # text_changed = ''.join(['<br>Hi ' + line for line in text2])
    # # (i used <br> to materialize a newline in the returned value)

    return render_template("todo.html",messages=todo)
@app.route('/logout')
def logout():
    logout_user()
    return render_template("index.html")



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)