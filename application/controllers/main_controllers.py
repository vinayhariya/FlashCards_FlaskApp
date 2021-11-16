from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_cont = Blueprint("main_cont", __name__, template_folder="../templates")


@main_cont.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main_cont.index"))


@main_cont.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.username)
