import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, render_register



# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gardendata.db")

# Main route to the landing page.
@app.route("/")
@login_required
def root():
    return render_template("landing_page.html")

# User is able to input a comment and see it posted with a seed in the gratitude garden
@app.route("/grateful-today", methods=["GET", "POST"])
@login_required
def grateful():
    if request.method == "POST":
        if not request.form.get("comment"):
            return apology("must provide gratitude comment", 403)
        comment=request.form.get("comment")
        ID = session.get("user_id")
        SQL = f"INSERT INTO gratitudes (UserID, Comment) VALUES ('{ID}', '{comment}');"
        rows = db.execute(SQL)
        return redirect("/gratitude-garden")
    else:
        ID = session.get("user_id")
        SQL5 = f"SELECT username FROM users WHERE id = {ID};"
        rows = db.execute(SQL5)
        username = rows[0]['username']
        return render_template("grateful-today.html", username=username)

# User is able to see the comments, date of comments, seeds planted
@app.route("/gratitude-garden")
@login_required
def gratitude():
    """Show history of transactions"""
    ID = session.get("user_id")
    SQL = f"SELECT * FROM gratitudes WHERE UserID = {ID};"
    rows = db.execute(SQL)
    # print(NewFlower)

    CommentsAndDates = []
    for row in rows:
        comment = row['Comment']
        date = row['DateOfPost']
        output = f"{comment}, {date}"
        CommentsAndDates.append(output)

    SQL5 = f"SELECT FlowerCount FROM users WHERE id = {ID};"
    rows = db.execute(SQL5)
    flowercount = rows[0]['FlowerCount']
    return render_template("gratitude-garden.html", FlowerCount=flowercount, CommentsAndDates=CommentsAndDates)

# User is able to click on an action to "water" their garden and see flowers appear in the garden
@app.route("/watering", methods=["GET", "POST"])
@login_required
def watering():
    if request.method == "POST":
        ID = session.get("user_id")
        SQL4 = f"UPDATE users SET FlowerCount = FlowerCount + 1 WHERE id = {ID};"
        db.execute(SQL4)
        return redirect("/gratitude-garden")
    else:
        return render_template("watering.html")

#User login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# User logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

#User registration with a 8-characters or greater password
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmed_password"):
            return apology("must provide confirmed password", 403)

        correct_password = request.form.get("password")
        confirmed_password = request.form.get("confirmed_password")
        user_name = request.form.get("username")
        if correct_password == confirmed_password:
            if len(correct_password) < 8:
                return apology("Password smashword, make it at least 8 letters long")
            hash_password = generate_password_hash(correct_password)
            # Input user information to database here
            SQL = f"INSERT INTO users (username, hash) VALUES ('{user_name}', '{hash_password}');"
            rows = db.execute(SQL)
            return redirect("/login")
        else:
            return apology("Passwords do not match", 403)

    return render_register()


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
