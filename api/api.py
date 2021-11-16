from flask_restful import Resource, reqparse
from api.models import Card, Deck, User
from api.database import db
from api.validation import BusinessValidationError
from api.custom_parsers import *
from api.custom_check_functions import *
import secrets


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

        user = User.query.filter(
            (User.user_id == user_id) & (User.api_key == api_key)).first()

        if user is None:
            return {"error": "User with username does not exist"}, 404

        deck_list = [{'deck_id': deck.deck_id, 'deck_name': deck.deckname,
                      'public': deck.public, 'no_of_cards': deck.no_of_cards()} for deck in user.decks]

        return {"decks": deck_list}

    def post(self):
        args = deck_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deckname = args["deckname"]
        public = args["public"]

        user = User.query.filter(
            (User.user_id == user_id) & (User.api_key == api_key)).first()

        if user is None:
            return {"error": "User with username does not exist"}, 404

        deck_present = Deck.query.filter(
            (Deck.user_id == user_id) & (Deck.deckname == deckname)).first()

        if deck_present:
            print('Present')
        else:
            print('Not present')
            new_deck = Deck(user_id=user_id, deckname=deckname,
                            public=bool(public))
            db.session.add(new_deck)
            db.session.commit()
            print('Deck commited properly')

        return {'sat': 'hi'}

    def delete(self):
        # TODO make it dynamic
        d = Deck.query.filter(Deck.deck_id == 1).first()
        db.session.delete(d)
        db.session.commit()
        pass


class UserOwnDeckCards(Resource):

    def get(self, user_id, api_key, deck_id):

        user = User.query.filter(
            (User.user_id == user_id) & (User.api_key == api_key)).first()

        if user is None:
            return {"error": "User with username does not exist"}, 404

        deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & (Deck.user_id == user_id)).first()

        if deck is None:
            return {"error": "No such deck exists for this user"}

        card_list = [{'card_id': card.card_id, 'front': card.front,
                      'back': card.back} for card in deck.cards]

        return {"deck_id": deck_id, 'no_of_cards': deck.no_of_cards(), "cards": card_list}

    pass

    def post(self):
        args = card_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        front = args["front"]
        back = args["back"]

        new_card = Card(front=front, back=back, deck_id=deck_id)

        db.session.add(new_card)
        db.session.commit()
        print('New Card added properly')
        pass

    def put(self):
        args = card_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        card_id = args["card_id"]
        front = args["front"]
        back = args["back"]

        u_card = Card.query.filter(
            (Card.deck_id == deck_id) & (Card.card_id == card_id)).first()

        if front:
            u_card.front = front
        if back:
            u_card.back = back

        db.session.add(u_card)
        db.session.commit()

    def delete(self):
        c = Card.query.filter(Card.card_id == 1).first()
        db.session.delete(c)
        db.session.commit()
        pass
