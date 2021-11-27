from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import login_required, current_user
import requests

main_cont = Blueprint("main_cont", __name__,
                      template_folder="../templates", static_folder="../static")


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

    status_code = res.status_code
    res = res.json()

    if status_code != 200:
        return f'{res["error_message"]}'

    attempted_res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/decks_attempted/get")

    status_code = attempted_res.status_code
    attempted_res = attempted_res.json()

    if status_code != 200:
        return f'{attempted_res["error_message"]}'

    return render_template("dashboard.html", name=current_user.username, decks=res["decks"], attempt=attempted_res["decks_attempted"])


@main_cont.route("/deck/deck_id=<int:deck_id>")
@login_required
def deckpage(deck_id):

    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/get")

    status_code = res.status_code
    res = res.json()

    if status_code != 200:
        flash(res["error_message"], 'warning')
        return redirect(url_for("main_cont.dashboard"))

    past_attempt_res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/score/get")

    status_code = past_attempt_res.status_code
    past_attempt_res = past_attempt_res.json()

    if status_code != 200:
        flash(past_attempt_res["error_message"], 'warning')
        return redirect(url_for("main_cont.dashboard"))

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

        status_code = res.status_code
        res = res.json()

        if status_code != 201:
            flash(res["error_message"], 'warning')
            return redirect(url_for("main_cont.add_new_deck"))

        flash(res["message"], 'success')
        return redirect(url_for("main_cont.dashboard"))


@main_cont.route("/deck/update/deck_id=<int:deck_id>", methods=["GET", "POST"])
@login_required
def updateDeck(deck_id):
    if request.method == "GET":
        res = requests.get(
            f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/get")

        status_code = res.status_code
        res = res.json()

        if status_code != 200:
            flash(res["error_message"], 'warning')
            return redirect(url_for("main_cont.deckpage"))

        deckname = res["deck_name"]

        return render_template("update_deck.html", deck_id=deck_id, deckname=deckname)
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

        status_code = res.status_code
        res = res.json()

        if status_code != 201:
            flash(res["error_message"], 'warning')
            return redirect(url_for("main_cont.updateDeck", deck_id=deck_id))

        flash(res["message"], 'success')
        return redirect(url_for("main_cont.deckpage", deck_id=deck_id))


@main_cont.route("/deck/delete/deck_id=<int:deck_id>")
@login_required
def deleteDeck(deck_id):

    res = requests.delete(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/delete")

    status_code = res.status_code
    res = res.json()

    if status_code != 200:
        flash(res["error_message"], 'warning')
    else:
        flash(res["message"], 'success')

    return redirect(url_for("main_cont.dashboard"))


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

        status_code = res.status_code
        res = res.json()

        if status_code != 201:
            flash(res["error_message"], 'warning')
            return redirect(url_for('main_cont.add_new_card', deck_id=deck_id))
        else:
            flash(res["message"], 'success')
            return redirect(url_for('main_cont.deckpage', deck_id=deck_id))


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

        status_code = res.status_code
        res = res.json()

        if status_code != 201:
            flash(res["error_message"], 'warning')
            return redirect(url_for('main_cont.update_card', deck_id=deck_id, card_id=card_id))
        else:
            flash(res["message"], 'success')
            return redirect(url_for('main_cont.view_deck_cards', deck_id=deck_id))


@main_cont.route("/deck/deck_id=<int:deck_id>/card/card_id=<int:card_id>/delete")
@login_required
def delete_card(deck_id, card_id):

    res = requests.delete(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/card_id={card_id}/delete")

    status_code = res.status_code
    res = res.json()

    if status_code != 200:
        flash(res["error_message"], 'warning')
    else:
        flash(res["message"], 'success')

    return redirect(url_for('main_cont.view_deck_cards', deck_id=deck_id))


@main_cont.route('/deck/deck-<int:deck_id>/cards/view')
@login_required
def view_deck_cards(deck_id):
    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/cardsList")

    status_code = res.status_code
    res = res.json()

    if status_code != 200:
        flash(res["error_message"], 'warning')
        return redirect(url_for("main_cont.deckpage", deck_id=deck_id))

    if res["no_of_cards"] == 0:
        flash('There are no cards in the deck', 'danger')
        return redirect(url_for("main_cont.deckpage", deck_id=deck_id))

    return render_template('view_deck_cards.html', cards=res['cards'], deck_id=res['deck_id'], creator=res['creator'])


@main_cont.route("/public_decks")
@login_required
def public_decks():
    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/publicDecks")

    status_code = res.status_code
    res = res.json()

    if status_code != 200:
        flash(res["error_message"], 'warning')
        return redirect(url_for("main_cont.dashboard"))

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

        if res.status_code != 200:
            flash(res["error_message"], 'warning')
            return redirect(url_for("main_cont.dashboard"))

        res = res.json()

        card_id = res["card"]["card_id"]

        if card_id == -1:
            session["solve_id"] = None
            flash(res["message"], 'success')
            return redirect(url_for('main_cont.deckpage', deck_id=deck_id))

        if session.get("solve_id", None) is None:
            session["solve_id"] = res["solve_id"]

        return render_template('study_card.html', card=res["card"], deck_id=deck_id, card_id=card_id)
    else:
        res = requests.get(
            f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/deck_id={deck_id}/card_id={card_id}/study/get")

        if res.status_code != 200:
            flash(res["error_message"], 'warning')
            return redirect(url_for("main_cont.dashboard"))

        res = res.json()

        if card_id == 0:
            session["solve_id"] = None

        card_id = res["card"]["card_id"]

        if card_id == -1:
            flash(res["message"], 'success')
            return redirect(url_for('main_cont.deckpage', deck_id=deck_id))

        return render_template('study_card.html', card=res, deck_id=deck_id, card_id=card_id)


@main_cont.route('/public_decks/author_name=<string:author_name>')
@login_required
def author_public_decks(author_name):
    res = requests.get(
        f"http://127.0.0.1:8000/api/user_id={current_user.user_id}/api_key={current_user.api_key}/publicDecks/author={author_name}/get")

    if res.status_code != 200:
        flash(res["error_message"], 'warning')
        return redirect(url_for("main_cont.dashboard"))

    res = res.json()

    if res["no_of_decks"] == 0:
        flash(f"There are no public decks of {author_name}", 'danger')
        return redirect(url_for("main_cont.dashboard"))

    return render_template("author_related_public_decks.html", author=author_name, decks=res["decks"])
