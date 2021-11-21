from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
import requests

main_cont = Blueprint("main_cont", __name__, template_folder="../templates")


@main_cont.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main_cont.dashboard"))


@main_cont.route("/dashboard")
@login_required
def dashboard():

    res = requests.get(
        f"http://127.0.0.1:8000/api/key={current_user.api_key}/user_id={current_user.user_id}/decks")

    if res.status_code == 200:
        # print('yes')
        pass
    else:
        print('error in the get request')
        return render_template("dashboard.html", name='Devil')

    res = res.json()

    if res["no_of_decks"] > 0:
        pass
    else:
        pass
    # print(res)
    return render_template("dashboard.html", name=current_user.username, decks=res["decks"])


@main_cont.route("/deckpage/id-<int:id>")
@login_required
def deckpage(id):
    res = requests.get(
        f"http://127.0.0.1:8000/api/{current_user.api_key}/user={current_user.user_id}/deck={id}/cards")
    res = res.json()
    return render_template("deckpage.html", name="Deck Page", deck=res)
    # return render_template("public_decks.html", name="Public Decks List", decks=res["decks"])


@main_cont.route("/deckpage/update/id-<int:id>", methods=["GET", "POST"])
@login_required
def updateDeck(id):
    if request.method == "GET":
        return render_template("update_deck_page.html", id=id)
    else:
        deckname = request.form.get("deckname")
        public = request.form.get("public")

        data = {"user_id": current_user.user_id, "api_key": current_user.api_key,
                "deckname": deckname, "public": public, "deck_id": id}

        res = requests.put("http://127.0.0.1:8000/api/decks/update", data)

        res = res.json()

        print("****************")
        print(res)
        print('Update')
        print("****************")
        return redirect(url_for('main_cont.deckpage', id=id))


@main_cont.route("/deckpage/delete/id-<int:id>", methods=["POST"])
@login_required
def deleteDeck(id):
    res = requests.delete(
        f"http://127.0.0.1:8000/api/key={current_user.api_key}/user_id={current_user.user_id}/delete/deck={id}")
    res = res.json()

    if res['sta'] == 'good':
        return redirect(url_for("main_cont.dashboard"))
    else:
        return 'No good'


@main_cont.route("/add_deck", methods=["GET", "POST"])
@login_required
def add_new_deck():
    print(request.method)
    if request.method == "GET":
        return render_template("add_new_deck_page.html")
    elif request.method == "POST":
        deckname = request.form.get("deckname")
        public = request.form.get("public")

        data = {"user_id": current_user.user_id, "api_key": current_user.api_key,
                "deckname": deckname, "public": public}

        res = requests.post("http://127.0.0.1:8000/api/decks/add", data)

        res = res.json()

        return redirect(url_for("main_cont.dashboard"))

    return 'added'


@main_cont.route("/public_decks")
@login_required
def publicDeckPage():
    res = requests.get("http://127.0.0.1:8000/api/decks/public")
    res = res.json()
    return render_template("public_decks.html", name="Public Decks List", decks=res["decks"])
