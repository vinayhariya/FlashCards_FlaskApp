from flask_restful import Resource, reqparse
from api.models import Card, Deck, Feedback, PerCard, SolvingDeck, User
from api.database import db
from api.validation import BusinessValidationError
from api.custom_parsers import *
from api.custom_check_functions import *
import secrets
from datetime import datetime
from sqlalchemy import desc


class UserLoginAPI(Resource):

    def get(self, user_id):  # TODO remove the get() function at the end
        user = User.query.filter(User.user_id == user_id).first()

        if user is None:
            return {"error": f"User with userid = {user_id} does not exist"}, 505

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "api_key": user.api_key,
        }

    def post(self):
        args = login_user_parser.parse_args()
        username = check_username(args["username"])
        password = check_password(args["password"])

        user = User.query.filter(
            (User.username == username) & (User.password == password)
        ).first()

        if user:
            return {"status": 200, "logged_in": True}
        else:
            raise BusinessValidationError(
                status_code=505,
                error_code="else",
                error_message="login error, details do not match",
            )


class UserRegisterAPI(Resource):

    def post(self):
        args = register_user_parser.parse_args()
        username = check_username(args["username"])
        password = check_password(args["password"])
        email = check_email(args["email"])

        user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if user:
            raise BusinessValidationError(
                status_code=505, error_code="else", error_message="duplicate user"
            )

        api_key = secrets.token_urlsafe(16)

        while User.query.filter(User.api_key == api_key).first():
            api_key = secrets.token_urlsafe(16)

        new_user = User(
            username=username, email=email, password=password, api_key=api_key
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            "user_id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "password": new_user.password,
        }


# properly coded till here


class UserOwnDeckList(Resource):

    def get(self, user_id, api_key):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        user = User.query.filter(User.user_id == user_id).first()

        deck_list = [{'deck_id': deck.deck_id, 'deck_name': deck.deckname,
                      'public': deck.public, 'no_of_cards': deck.no_of_cards()} for deck in user.decks]

        return {"no_of_decks": user.no_of_decks(), "decks": deck_list}

    def post(self):
        args = deck_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deckname = args["deckname"]
        public = args["public"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        deck_present = Deck.query.filter(
            (Deck.author_id == user_id) & (Deck.deckname == deckname)).first()

        if deck_present:
            print('Present')
        else:
            print('Not present')
            new_deck = Deck(author_id=user_id, deckname=deckname,
                            public=bool(public))
            db.session.add(new_deck)
            db.session.commit()
            print('Deck commited properly')

        return {'sat': 'hi'}

    def delete(self, user_id, api_key, deck_id):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        d = Deck.query.filter(Deck.deck_id == deck_id).first()
        db.session.delete(d)
        db.session.commit()

        return {'sta': 'good'}

    def put(self):
        args = deck_updation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deckname = args["deckname"]
        public = args["public"]
        deck_id = args["deck_id"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        u_deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & (Deck.author_id == user_id)).first()

        if deckname:
            u_deck.deckname = deckname
        u_deck.public = bool(public)

        db.session.add(u_deck)
        db.session.commit()

        return 'Success'


class UserOwnDeckCards(Resource):

    def get(self, user_id, api_key, deck_id):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & ((Deck.author_id == user_id) | (Deck.public == True))).first()

        if deck is None:
            return {"error": "No such deck exists for this user"}

        card_list = [{'card_id': card.card_id, 'front': card.front,
                      'back': card.back} for card in deck.cards]

        return {'deck_id': deck.deck_id, 'deck_name': deck.deckname, 'public': deck.public, 'no_of_cards': deck.no_of_cards(), "cards": card_list}

    pass

    def post(self):
        args = card_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        front = args["front"]
        back = args["back"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        new_card = Card(front=front, back=back, deck_id=deck_id)

        db.session.add(new_card)
        db.session.commit()
        print('New Card added properly')
        pass

    def put(self):
        args = card_updation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        card_id = args["card_id"]
        front = args["front"]
        back = args["back"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        u_card = Card.query.filter(
            (Card.deck_id == deck_id) & (Card.card_id == card_id)).first()

        if front:
            u_card.front = front
        if back:
            u_card.back = back

        db.session.add(u_card)
        db.session.commit()

    def delete(self, user_id, api_key, deck_id, card_id):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        c = Card.query.filter((Card.card_id == card_id) &
                              (Card.deck_id == deck_id)).first()
        db.session.delete(c)
        db.session.commit()

        return {'sta_delete_card': 'good'}


class PublicDecks(Resource):
    def get(self, user_id, api_key):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        decks = Deck.query.filter(Deck.public == True).all()

        deck_list = [{'deck_id': deck.deck_id, 'deck_name': deck.deckname,
                      'public': deck.public, 'no_of_cards': deck.no_of_cards(), "author": deck.get_author()} for deck in decks]

        print(deck_list)
        return {"no_of_decks": len(deck_list), "decks": deck_list}


class GettingCard(Resource):
    def get(self, user_id, api_key, deck_id, card_id):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        # if card_id == 0:
        #     sd = SolvingDeck(user_id=user_id, deck_id=deck_id,
        #                      start_time=datetime.now())
        #     db.session.add(sd)
        #     db.session.commit()
        #     print(sd.solve_id)

        card = Card.query.filter((Card.deck_id == deck_id) & (
            Card.card_id > card_id)).first()

        if card is None:
            return {'card_id': -1}
        return {'card_id': card.card_id, 'front': card.front, 'back': card.back}

    def post(self):
        args = solving_deck_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        card_id = args["card_id"]
        solve_id = args["solve_id"]
        feedback = args["feedback"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        if solve_id is None:
            sd = SolvingDeck(user_id=user_id, deck_id=deck_id,
                             start_time=datetime.now())
            db.session.add(sd)
            db.session.commit()
            solve_id = sd.solve_id

        feedback_obj = Feedback.query.filter(
            Feedback.feedback_desc == feedback).first()

        pc = PerCard(solve_id=solve_id, card_id=card_id,
                     feedback=feedback_obj.feedback_id)
        db.session.add(pc)

        sd = SolvingDeck.query.filter(SolvingDeck.solve_id == solve_id).first()
        sd.total_score += pc.getScore()
        sd.time_taken_mins = round(
            (datetime.now() - sd.start_time).total_seconds() / 60, 2)
        db.session.add(sd)

        db.session.commit()

        card = Card.query.filter((Card.deck_id == deck_id) & (
            Card.card_id > card_id)).first()

        if card is None:
            return {"card": {'card_id': -1}}

        return {"solve_id": solve_id, "card": {'card_id': card.card_id, 'front': card.front, 'back': card.back}}


class GetScoreForDeck(Resource):

    def get(self, user_id, api_key, deck_id):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        r = SolvingDeck.query.filter((SolvingDeck.user_id == user_id) & (
            SolvingDeck.deck_id == deck_id)).order_by(desc(SolvingDeck.start_time)).all()

        return {
            'user_id': user_id,
            'deck_id': deck_id,
            'rows': [
                {
                    "date": record.start_time.strftime("%d-%b-%Y"),
                    "start_time": record.start_time.strftime("%I:%M:%S %p"),
                    "time_taken": record.time_taken_mins,
                    "total_score": record.total_score
                }
                for record in r
            ]
        }


class GetDecksAttempted(Resource):
    def get(self, user_id, api_key):

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        r = SolvingDeck.query.filter(SolvingDeck.user_id == user_id).order_by(
            desc(SolvingDeck.start_time)).all()

        return {
            'user_id': user_id,
            'decks_attempted': [
                {
                    'deckname': record.solvedecks_r.deckname,
                    'date': record.start_time.strftime("%d-%b-%Y"),
                    'author': record.solvedecks_r.author.username,
                    "total_score": record.total_score
                }
                for record in r
            ]
        }
