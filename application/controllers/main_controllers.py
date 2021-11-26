from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import login_required, current_user
import requests

main_cont = Blueprint("main_cont", __name__, template_folder="../templates", static_folder="../static")

# TODO change the part just after the request after fixing the api


@main_cont.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main_cont.dashboard"))


@main_cont.route("/dashboard")
@login_required
def dashboard():

    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/decksList")

    if res.status_code != 200:
        return 'error in the get request in the main.cont -> dashboard'  # TODO

    res = res.json()

    attempted_res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/decks_attempted/get")
    attempted_res = attempted_res.json()

    return render_template("dashboard.html", name=current_user.username, decks=res["decks"], attempt=attempted_res["decks_attempted"])


@main_cont.route("/deck/deck_id=<int:deck_id>")
@login_required
def deckpage(deck_id):

    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/get")

    res = res.json()

    past_attempt_res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/score/get")
    past_attempt_res = past_attempt_res.json()

    return render_template("deckpage.html", name="Deck Page", deck=res, card_id=0, attempt=past_attempt_res['rows'])


@main_cont.route("/add_deck", methods=["GET", "POST"])
@login_required
def add_new_deck():
    if request.method == "GET":
        return render_template("add_new_deck.html")
    elif request.method == "POST":
        deckname = request.form.get("deckname")
        public = request.form.get("public")

        data = {
            "user_id": current_user.user_id,
            "api_key": current_user.api_key,
            "deckname": deckname,
            "public": public
        }

        res = requests.post("http://127.0.0.1:8000/api/deck/add", data)

        res = res.json()

        return redirect(url_for("main_cont.dashboard"))


@main_cont.route("/deck/update/deck_id=<int:deck_id>", methods=["GET", "POST"])
@login_required
def updateDeck(deck_id):
    if request.method == "GET":
        return render_template("update_deck.html", deck_id=deck_id)
    else:
        deckname = request.form.get("deckname")
        public = request.form.get("public")

        data = {
            "user_id": current_user.user_id,
            "api_key": current_user.api_key,
            "deckname": deckname,
            "public": public,
            "deck_id": deck_id
        }

        res = requests.put("http://127.0.0.1:8000/api/deck/update", data)

        res = res.json()

        return redirect(url_for('main_cont.deckpage', deck_id=deck_id))


@main_cont.route("/deck/delete/deck_id=<int:deck_id>")
@login_required
def deleteDeck(deck_id):

    res = requests.delete(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/delete")

    res = res.json()

    if res['sta'] == 'good':
        return redirect(url_for("main_cont.dashboard"))
    else:
        return 'No good'


@main_cont.route('/add_card/deck_id=<int:deck_id>', methods=['GET', 'POST'])
@login_required
def add_new_card(deck_id):
    if request.method == "GET":
        return render_template("add_new_card.html", deck_id=deck_id)
    else:
        card_front = request.form.get("card_front")
        card_back = request.form.get("card_back")

        data = {
            "user_id": current_user.user_id,
            "api_key": current_user.api_key,
            "deck_id": deck_id,
            "front": card_front,
            "back": card_back
        }

        res = requests.post("http://127.0.0.1:8000/api/deck/card/add", data)

        res = res.json()

        return redirect(url_for('main_cont.deckpage', deck_id=deck_id))


@main_cont.route("/deck/deck_id=<int:deck_id>/card/card_id=<int:card_id>/delete")
@login_required
def delete_card(deck_id, card_id):

    res = requests.delete(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/card_id={card_id}/delete")
    res = res.json()

    if res['sta_delete_card'] == 'good':
        return redirect(url_for("main_cont.view_deck_cards", deck_id=deck_id))
    else:
        return 'No good'


@main_cont.route('/deck/deck_id=<int:deck_id>/update_card/card_id=<int:card_id>', methods=['GET', 'POST'])
@login_required
def update_card(deck_id, card_id):
    if request.method == "GET":
        return render_template("update_card.html", deck_id=deck_id, card_id=card_id)
    else:
        card_front = request.form.get("card_front")
        card_back = request.form.get("card_back")

        data = {
            "user_id": current_user.user_id,
            "api_key": current_user.api_key,
            "card_id": card_id,
            "deck_id": deck_id,
            "front": card_front,
            "back": card_back
        }

        res = requests.put("http://127.0.0.1:8000/api/deck/card/update", data)

        res = res.json()

        return redirect(url_for('main_cont.view_deck_cards', deck_id=deck_id))


@main_cont.route('/deck/deck-<int:deck_id>/cards/view')
@login_required
def view_deck_cards(deck_id):
    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/cardsList")
    res = res.json()

    return render_template('view_deck_cards.html', cards=res['cards'], deck_id=res['deck_id'], creator=res['creator'])


@main_cont.route("/public_decks")
@login_required
def public_decks():
    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/publicDecks")
    res = res.json()
    return render_template("public_decks.html", name="Public Decks List", decks=res["decks"])


@main_cont.route('/study/deck/deck_id=<int:deck_id>/card_id=<int:card_id>', methods=['GET', 'POST'])
@login_required
def studyCard(deck_id, card_id):
    if request.method == 'POST':
        feedback = request.form.get("feedback")

        data = {
            "user_id": current_user.user_id,
            "api_key": current_user.api_key,
            "deck_id": deck_id,
            "card_id": card_id,
            "solve_id": session.get("solve_id", None),
            "feedback": feedback
        }

        res = requests.post("http://127.0.0.1:8000/api/deck/study", data)

        res = res.json()

        card_id = res["card"]["card_id"]

        if card_id == -1:
            session["solve_id"] = None
            # /return 'Finish'
            return redirect(url_for('main_cont.deckpage', deck_id=deck_id))

        if session.get("solve_id", None) is None:
            session["solve_id"] = res["solve_id"]

        return render_template('study_card.html', card=res["card"], deck_id=deck_id, card_id=card_id)
    else:
        res = requests.get(
            f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/card_id={card_id}/study/get")

        res = res.json()

        if card_id == 0:
            session["solve_id"] = None

        card_id = res["card_id"]

        if card_id == -1:
            return redirect(url_for('main_cont.deckpage', deck_id=deck_id))

        return render_template('study_card.html', card=res, deck_id=deck_id, card_id=card_id)


@main_cont.route('/public_decks/author_name=<string:author_name>')
@login_required
def author_public_decks(author_name):
    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/publicDecks/author={author_name}/get")
    res = res.json()
    return render_template("author_related_public_decks.html", author=author_name, decks=res["decks"])
