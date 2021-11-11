from .database import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    decks = db.relationship("Deck")
    pass


class Deck(db.Model):
    __tablename__ = "decks"

    deck_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    deckname = db.Column(db.String(25), nullable=False, unique=True)
    public = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    cards = db.relationship("Card")
    pass


class Card(db.Model):
    __tablename__ = "cards"

    card_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    front = db.Column(db.String(255), nullable=False)
    back = db.Column(db.String(255), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    pass


class SolvingDeck(db.Model):
    __tablename__ = "solving_deck"

    solve_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    total_score = db.Column(db.Integer, nullable=True)

    card_unique_details = db.relationship("PerCard")
    pass


class PerCard(db.Model):
    __tablename__ = "per_card"

    per_card_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    solve_id = db.Column(
        db.Integer, db.ForeignKey("solving_deck.solve_id"), nullable=False
    )
    card_id = db.Column(db.Integer, db.ForeignKey("cards.card_id"), nullable=False)
    difficulty = db.Column(
        db.String(2), db.ForeignKey("difficulty.difficulty_id"), nullable=False
    )
    score = db.Column(db.Integer, db.ForeignKey("scoring.score_id"), nullable=False)


class Difficulty(db.Model):
    __tablename__ = "difficulty"

    difficulty_id = db.Column(db.String(2), primary_key=True)
    difficulty_desc = db.Column(db.String(15), unique=True, nullable=False)
    pass


class Scoring(db.Model):
    __tablename__ = "scoring"

    score_id = db.Column(db.Integer, primary_key=True)
    score_desc = db.Column(db.String(15), unique=True, nullable=False)
    pass


# db.create_all()
