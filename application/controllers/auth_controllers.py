from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
import requests

from api.models import User

auth = Blueprint("auth", __name__,
                 template_folder="../templates/auth_templates")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember")

        data = {"username": username, "password": password}

        res = requests.post("http://127.0.0.1:8000/api/user/login", data)

        status_code = res.status_code
        res = res.json()

        if status_code == 200:
            username = username.strip().title()
            user = User.query.filter(User.username == username).first()
            login_user(user, remember=remember)
            return redirect(url_for("main_cont.dashboard"))
        else:
            flash(res["error_message"], 'warning')

            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        data = {
            "new": str(True),
            "username": username,
            "email": email,
            "password": password,
        }

        res = requests.post("http://127.0.0.1:8000/api/user/register", data)

        status_code = res.status_code
        res = res.json()

        if status_code == 201:
            flash("New User created. Login to continue.", 'success')
            return redirect(url_for("auth.login"))
        else:
            flash(res["error_message"], 'danger')
            return redirect(url_for("auth.signup"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_cont.index"))
