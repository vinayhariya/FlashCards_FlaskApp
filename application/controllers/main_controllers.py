from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_cont = Blueprint("main_cont", __name__, template_folder="../templates")


@main_cont.route("/")
def index():
    return render_template("index.html")


@main_cont.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.username)
