from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
import requests

from api.models import User

auth = Blueprint("auth", __name__, template_folder="templates")


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_cont.index"))


@auth.route("/signup", methods=["POST"])
def signup_post():

    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    data = {"username": name, "email": email, "password": password}

    res = requests.post("http://127.0.0.1:8000/api/user", data)

    res = res.json()

    if res.get("error_code", None):
        flash("Account address already exists")
        return redirect(url_for("auth.signup"))

    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["POST"])
def login_post():

    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter(User.email == email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    # if not user or not check_password_hash(user.password, password):
    #     flash('Please check your login details and try again.')
    #     return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=True)
    return redirect(url_for("main_cont.profile"))
    