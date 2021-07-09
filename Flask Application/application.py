import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from tempfile import mkdtemp

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
db = SQL("sqlite:///data.db")

@app.route("/")
def index():
    if session.get("user_id") == None:
        return redirect("/login")
    else:
        tasks = db.execute("SELECT * FROM tasks WHERE id = ? ORDER BY date(date)", session["user_id"])
        if len(tasks) == 0:
            return render_template("empty.html")
        else:
            return render_template("index.html", tasks=tasks)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username)
        if not username:
            flash("Please input your username")
            return render_template("login.html")
        elif not password:
            flash("Please input your password")
            return render_template("login.html")
        else:
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)
            hashed = generate_password_hash(password, method = "pbkdf2:sha256", salt_length = 8)
            if len(rows) != 1:
                flash("Your username is invalid")
                return render_template("login.html")
            elif not check_password_hash(rows[0]["hash"], password):
                flash("You password is invalid")
                return render_template("login.html")
            else:
                session["user_id"] = rows[0]["id"]
                print(session["user_id"])
                return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("rusername")
        password = request.form.get("rpassword")
        confirm = request.form.get("crpassword")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not username:
            flash("Please enter a username")
            return redirect("/register")
        else:
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)
            if not password:
                flash("Please enter a password")
                return redirect("/register")
            elif not confirm:
                flash("Please enter a confirmation password")
                return redirect("/register")
            elif len(rows) != 0:
                flash("Sorry. The username has been taken")
                return redirect("/register")
            elif password != confirm:
                flash("Your passwords do not match")
                return redirect("/register")
            else:
                hashs = generate_password_hash(password, method = "pbkdf2:sha256", salt_length = 8)
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, hashs)
                flash(f"Successfully registered as {username}! Please login.")
                return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/add", methods = ["GET", "POST"])
def add():
    if session.get("user_id") == None:
        return redirect("/login")
    else:
        if request.method == "POST":
            title = request.form.get("title")
            desc = request.form.get("description")
            date = request.form.get("date")
            if not title:
                flash("Please input a title")
                return redirect("/add")
            elif not desc:
                flash("Please input a description")
                return redirect("/add")
            elif not date:
                flash("Please input a date")
                return redirect("/add")
            else:
                db.execute("INSERT INTO tasks (id, task, description, date) VALUES (?, ?, ?, ?);", session["user_id"], title, desc, date)
                tasks = db.execute("SELECT * FROM tasks WHERE id = ?", session["user_id"])
                return redirect("/")
        else:
            return render_template("add.html")

@app.route("/edit/<string:id2>/", methods = ["GET", "POST"])
def edit(id2):
    if session.get("user_id") == None:
        return redirect("/login")
    else:
        if request.method == "POST":
            db.execute("DELETE FROM tasks WHERE id2 = ?;", int(id2))
            tasks = db.execute("SELECT * FROM tasks WHERE id = ?;", session["user_id"])
            return redirect("/")
        else:
            title = db.execute("SELECT task FROM tasks WHERE id2 = ?;", int(id2))
            desc = db.execute("SELECT description FROM tasks WHERE id2 = ?;", int(id2))
            return render_template("edit.html", title=title[0]["task"], description=desc[0]["description"], id2=int(id2))

@app.route("/logout")
def logout():
    if session.get("user_id") != None:
        session.clear()
    return redirect("/login")