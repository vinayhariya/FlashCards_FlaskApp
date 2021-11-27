from sqlalchemy.orm import backref
from sqlalchemy import event
from .database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"

    def get_id(self):
        '''
        Added due to the flask_login login manager
        '''
        return (self.user_id)

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(35), nullable=False, unique=True)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    api_key = db.Column(db.String(16), nullable=False)

    db.relationship("Deck")

    def no_of_decks(self):
        return len(self.decks)


class Deck(db.Model):
    __tablename__ = "decks"

    deck_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    deckname = db.Column(db.String(40), nullable=False)
    public = db.Column(db.Boolean, nullable=False, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey(
        "users.user_id"), nullable=False)

    db.relationship("Card")

    author = db.relationship("User", backref=backref(
        "decks", cascade="all,delete"))

    def no_of_cards(self):
        return len(self.cards)

    def get_author(self):
        return self.author.username


class Card(db.Model):
    __tablename__ = "cards"

    card_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey(
        "decks.deck_id"), nullable=False)

    deck = db.relationship("Deck", backref=backref(
        "cards", cascade="all,delete"))


class SolvingDeck(db.Model):
    __tablename__ = "solving_deck"

    solve_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.user_id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey(
        "decks.deck_id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    time_taken_mins = db.Column(db.Float, nullable=True)
    total_score = db.Column(db.Integer, nullable=True, default=0)

    db.relationship("PerCard")

    solvedecks_r = db.relationship("Deck", backref=backref(
        "solving_deck", cascade="all,delete"))


class PerCard(db.Model):
    __tablename__ = "per_card"

    per_card_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    solve_id = db.Column(
        db.Integer, db.ForeignKey("solving_deck.solve_id"), nullable=False
    )
    card_id = db.Column(db.Integer, db.ForeignKey(
        "cards.card_id"), nullable=False)
    feedback = db.Column(
        db.Integer, db.ForeignKey("feedback.feedback_id"), nullable=False
    )

    f = db.relationship("Feedback")

    def getScore(self):
        return self.f.score

    perdeck_r = db.relationship("SolvingDeck", backref=backref(
        "per_card", cascade="all,delete"))

    percard_r = db.relationship("Card", backref=backref(
        "per_card", cascade="all,delete"))


class Feedback(db.Model):
    __tablename__ = "feedback"

    feedback_id = db.Column(db.Integer, primary_key=True)
    feedback_desc = db.Column(db.String(15), unique=True, nullable=False)
    score = db.Column(db.Integer, nullable=False)


@event.listens_for(Feedback.__table__, 'after_create')
def create_departments(*args, **kwargs):
    db.session.add(Feedback(feedback_desc="Easy", score=3))
    db.session.add(Feedback(feedback_desc="Medium", score=1))
    db.session.add(Feedback(feedback_desc="Difficult", score=0))
    db.session.commit()
# above method is used only when a new database file is generated and the feedback table as to be filled
