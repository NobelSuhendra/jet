# Just Enough Tasks
> This is my final project for CS50's Introduction To Computer Science

## What is Just Enough Tasks?
**Just Enough Tasks** is a Flask web application that serves as simple task manager. It focuses on **simplicity** and **prioritising** more important tasks.

## SQLite
- All data is stored in **data.db**
- In the *users* table, the **username**, **hashed password** and **id** is stored, where **id** is the *primary key*.
```sql
CREATE TABLE users (username TEXT, hash TEXT, id INTEGER, PRIMARY KEY(id));
```
- In the *tasks* table, an **id**, **title** (as task), **description**, **due date** (as date) and **task id** (as id2) is stored, where **task id** is the *primary key*.
```sql
CREATE TABLE tasks(id INTEGER, task TEXT, description TEXT, date TEXT, id2 INTEGER, PRIMARY KEY(id2));
```

##  Templates
#### 1. layout.html
- This layout is used in **edit.html** only.

#### 2. layout2.html
- This layout is used in **register.html** and **login.html**.

#### 3. layout3.html
- This layout is used in **add.html**, **edit.html** and **index.html**.

#### 4. add.html
- This is where tasks are *added*.
- It consists of a form containing input fields for a **title**, **description**, and **date**.

#### 5. edit.html
- This is where tasks can be *deleted/completed*.
- It displays the **title** and **description** of the task and has a button to *delete/complete* the task.

#### 6. empty.html
- This is the file that the **/** route renders if the task list is *empty*.

#### 7. index.html
- This is the file that the **/** route renders if there are tasks *added*.
- It consists of a **table** that displays all the information about the task.

#### 8. login.html
- This is where people can **login** to existing accounts.

#### 9. register.html
- This is where people can **register** for a new account.

## Routes
#### 1. /
- This is the route for the **home** page.
- It renders **index.html** if there are tasks and **empty.html** if there are none.
```python
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
```

#### 2. /login
- This is the route for the **login** page.
- It ensures that the **username** and **password** provided is valid.
```python
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
```

#### 3. /register
- This is the route for the **register** page.
- It ensures that the **username** has not been taken.
```python
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
```

#### 4. /add
- This is the route for the **add** page.
- It allows users to add new tasks.
```python
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
```
#### 5. edit/string:id2
- This is the route for the **edit** page for each task.
- It allows users to *complete/delete* a task.
```python
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
```

#### 6. /logout
- Redirects to the **/login** route
```python
@app.route("/logout")
def logout():
    if session.get("user_id") != None:
        session.clear()

    return redirect("/login")
```

## Demonstration URL
https://youtu.be/8T3PlQS3UNI
