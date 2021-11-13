from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
import requests

from api.models import User

auth = Blueprint("auth", __name__, template_folder="templates")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":  # after the form has been submitted
        username = request.form.get("username")
        password = request.form.get("password")

        data = {"username": username, "password": password}

        res = requests.post("http://127.0.0.1:8000/api/user", data)

        res = res.json()

        if res.get("status", None):  # logged in successfully
            user = User.query.filter(User.username == username).first()
            login_user(user, remember=True)
            return redirect(url_for("main_cont.profile"))
        else:
            flash("Please check your login details and try again.")
            return redirect(
                url_for("auth.login")
            )  # if the user doesn't exist or password is wrong, reload the page
    else:
        return "Not Allowed Login"  # remove later


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")

        data = {
            "new": str(True),
            "username": name,
            "email": email,
            "password": password,
        }

        res = requests.post("http://127.0.0.1:8000/api/user", data)

        res = res.json()

        if res.get("error_code", None):
            flash("Account address already exists")
            return redirect(url_for("auth.signup"))

        flash("New User created. Login to continue.")
        return redirect(url_for("auth.login"))
    else:
        return "Not Allowed SignUp"  # remove later


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_cont.index"))
