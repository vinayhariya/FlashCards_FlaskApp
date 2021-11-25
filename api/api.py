from flask_restful import Resource
from api.models import Card, Deck, Feedback, PerCard, SolvingDeck, User
from api.database import db
from api.validation import BusinessValidationError
from api.custom_parsers import *
from api.custom_check_functions import *
import secrets
from datetime import datetime
from sqlalchemy import desc


class UserLoginAPI(Resource):
    """
    For Login
    """

    def get(self, user_id):  # TODO remove the get() function at the end
        """To get the credentials of the user requested

        Args:
            user_id (int): id of the user (used in the database)

        Returns:
            [type]: [description]
        """
        user = User.query.filter(User.user_id == user_id).first()

        if user is None:
            # TODO put proper error
            return {"error": f"User with userid = {user_id} does not exist"}, 505

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "api_key": user.api_key,
        }

    def post(self):
        """To securly check the credentials of the user

        Raises:
            BusinessValidationError: In case of mismatch of details

        Returns:
            [type]: [description]
        """
        args = login_user_parser.parse_args()
        username = check_username(args["username"])
        password = check_password(args["password"])

        user = User.query.filter(
            (User.username == username) & (User.password == password)
        ).first()

        if user:
            # TODO put proper
            return {"status": 200, "logged_in": True}
        else:
            raise BusinessValidationError(
                status_code=505,
                error_code="else",
                error_message="login error, details do not match",
            )


class UserRegisterAPI(Resource):
    """
    For Register
    """

    def post(self):
        """Creating a new user

        Raises:
            BusinessValidationError: if the details are duplicate

        Returns:
            [type]: [description]
        """
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
            "stat": "good"
        }  # TODO check if this is the best way to send the data back


class UserDeckList(Resource):
    """
    For getting the list of decks created by the user
    """

    def get(self, user_id, api_key):
        """Used to get the list of decks created by the user

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        user = User.query.filter(User.user_id == user_id).first()

        deck_list = [
            {'deck_id': deck.deck_id,
             'deck_name': deck.deckname,
             'public': deck.public,
             'no_of_cards': deck.no_of_cards()
             }
            for deck in user.decks
        ]

        return {
            "no_of_decks": user.no_of_decks(),
            "decks": deck_list
        }  # TODO check if this is the best way to send the data back


class DeckResource(Resource):
    """
    Deck CRUD operation (for decks related to the user)
    """

    def get(self, user_id, api_key, deck_id):
        """Used to get information about a certain deck such as its creator, name, visibilty to the public, number of cards. (READ)

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & ((Deck.author_id == user_id) | (Deck.public == True))).first()

        if deck is None:
            # TODO put proper error
            return {"error": "No such deck exists for this user"}

        creator = deck.author_id == user_id

        return {
            'creator': creator,
            'deck_id': deck.deck_id,
            'deck_name': deck.deckname,
            'public': deck.public,
            'no_of_cards': deck.no_of_cards()
        }  # TODO check if this is the best way to send the data back

    def post(self):
        """Used to enter into of a new deck into the database (CREATE) 

        Returns:
            [type]: [description]
        """
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
            # TODO add an error code here for duplicate name for that particular user
            print('Duplicate deck name present')
        else:
            new_deck = Deck(author_id=user_id,
                            deckname=deckname, public=bool(public))
            db.session.add(new_deck)
            db.session.commit()

        return {'sat': 'hi'}  # TODO send back proper response

    def put(self):
        """Used for updating the information of the exisiting deck (UPDATE)

        Returns:
            [type]: [description]
        """
        args = deck_updation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        deckname = args["deckname"]
        public = args["public"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        u_deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & (Deck.author_id == user_id)).first()

        if not u_deck:  # deck does not exist
            # TODO give proper error message
            return 'Deck does not exist'

        if deckname:

            duplicate_deck_name = Deck.query.filter(
                (Deck.author_id == user_id) & (Deck.deckname == deckname)).first()

            if duplicate_deck_name:  # if a deck with that name already exists
                # TODO give proper error message
                return 'Deck name should not be duplicate'

            u_deck.deckname = deckname

        u_deck.public = bool(public)

        db.session.add(u_deck)
        db.session.commit()

        return 'Success'  # TODO send back proper response

    def delete(self, user_id, api_key, deck_id):
        """Used to delete the specific deck requested (DELETE)

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Returns:
            [type]: [description]
        """
        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        deck_exists = Deck.query.filter(
            (Deck.author_id == user_id) & (Deck.deck_id == deck_id)).first()

        if not deck_exists:
            # TODO give proper error message
            return 'Deck either not there or does not belong to the user'

        db.session.delete(deck_exists)
        db.session.commit()

        return {'sta': 'good'}  # TODO send back proper response


class DeckCardList(Resource):

    def get(self, user_id, api_key, deck_id):
        """Used to get the list of cards of a particular deck

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & ((Deck.author_id == user_id) | (Deck.public == True))).first()

        if deck is None:
            # TODO give proper error message
            return {"error": "No such deck exists for this user"}

        card_list = [
            {'card_id': card.card_id,
             'front': card.front,
             'back': card.back
             }
            for card in deck.cards
        ]

        return {
            'creator': deck.author_id == user_id,
            'deck_id': deck.deck_id,
            'deck_name': deck.deckname,
            'public': deck.public,
            'no_of_cards': deck.no_of_cards(),
            "cards": card_list
        }  # TODO check if this is the best way to send the data back


class CardResource(Resource):
    """
    Card CRUD operation (for cards related to a specific deck) \n
    Create, Delete, Update operations can only be done by the 'creator' user \n
    Read is possible for the 'creator' user and also for other users of the deck is public \n
    """

    def get(self, user_id, api_key, card_id):
        """Used to get a particular card created by user or part of a public deck (READ)

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            card_id (int): id of the specific card requested

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        card = Card.query.filter(Card.card_id == card_id).first()

        if not card:
            # TODO give proper error message
            return {"error": "No such card exists"}

        if not card.deck.public:
            if not (card.deck.author_id == user_id):
                # TODO give proper error message
                return {"error": "No such card exists for this user"}

        return{
            'creator': card.deck.author_id == user_id,
            'deck_id': card.deck.deck_id,
            'deck_name': card.deck.deckname,
            'card_id': card.card_id,
            'card_front': card.front,
            'card_back': card.back
        }  # TODO check if this is the best way to send the data back

    def post(self):
        """Used to create a new card to be part of a deck created by user (CREATE)

        Returns:
            [type]: [description]
        """
        args = card_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        front = args["front"]
        back = args["back"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        deck = Deck.query.filter((Deck.deck_id == deck_id) & (
            Deck.author_id == user_id)).first()

        if not deck:
            # TODO give proper error message
            return {"error": "No such deck exists for this user"}

        card = Card.query.filter((Card.deck_id == deck_id) & (
            (Card.front == front) | (Card.back == back))).first()

        if card:
            # TODO give proper error message
            return {"error": "Duplicate Card for this deck"}

        new_card = Card(front=front, back=back, deck_id=deck_id)

        db.session.add(new_card)
        db.session.commit()

        return {'sat': 'hi'}  # TODO send back proper response

    def put(self):
        """Used to update a particular card of a deck (UPDATE)

        Returns:
            [type]: [description]
        """
        args = card_updation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        card_id = args["card_id"]
        front = args["front"]
        back = args["back"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        card = Card.query.filter(
            (Card.deck_id == deck_id) & (Card.card_id == card_id)).first()

        if not card:
            # TODO give proper error message
            return {"error": "Card does not exist"}

        if not (card.deck.author_id == user_id):
            # TODO give proper error message
            return {"error": "Card does not exist for this user"}

        if front:
            c = Card.query.filter((Card.deck_id == deck_id)
                                  & (Card.front == front)).first()

            if c:
                # TODO give proper error message
                return {"error": "Card duplaicate with new front"}

            card.front = front

        if back:

            c = Card.query.filter((Card.deck_id == deck_id)
                                  & (Card.back == back)).first()

            if c:
                # TODO give proper error message
                return {"error": "Card duplaicate with new back"}

            card.back = back

        db.session.add(card)
        db.session.commit()

        return {'sat': 'hi'}  # TODO send back proper response

    def delete(self, user_id, api_key, deck_id, card_id):
        """Used to delete a particular card from a deck (DELETE)

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested
            card_id (int): id of the specific card requested

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        c = Card.query.filter((Card.card_id == card_id) &
                              (Card.deck_id == deck_id)).first()

        if not c:
            # TODO give proper error message
            return {"error": "Card does not exist"}

        if not c.deck.author_id == user_id:
            # TODO give proper error message
            return {"error": "Card does not exist for this user"}

        db.session.delete(c)
        db.session.commit()

        return {'sta_delete_card': 'good'}  # TODO send back proper response


class PublicDecks(Resource):
    def get(self, user_id, api_key):
        """To get all the public decks available

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        decks = Deck.query.filter(Deck.public == True).all()

        deck_list = [
            {'deck_id': deck.deck_id,
             'deck_name': deck.deckname,
             'public': deck.public,
             'no_of_cards': deck.no_of_cards(),
             "author": deck.get_author()
             }
            for deck in decks
        ]

        # TODO send back proper response
        return {"no_of_decks": len(deck_list), "decks": deck_list}


class UserDeckScore(Resource):

    def get(self, user_id, api_key, deck_id):
        """To get all the scores made by the user of a specific deck in order of the latest attempt

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        times_solved = SolvingDeck.query.filter((SolvingDeck.user_id == user_id) & (
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
                for record in times_solved
            ]
        }  # TODO check if this is the best way to send the data back


class UserDeckAttempted(Resource):

    def get(self, user_id, api_key):
        """To get all the decks attempted by the user order of the latest attempt

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made

        Returns:
            [type]: [description]
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        decks_attempted = SolvingDeck.query.filter(
            SolvingDeck.user_id == user_id).order_by(desc(SolvingDeck.start_time)).all()

        return {
            'user_id': user_id,
            'decks_attempted': [
                {
                    'creator': record.solvedecks_r.author_id == user_id,
                    'deck_id': record.solvedecks_r.deck_id,
                    'public': record.solvedecks_r.public,
                    'deckname': record.solvedecks_r.deckname,
                    'date': record.start_time.strftime("%d-%b-%Y"),
                    'author': record.solvedecks_r.author.username,
                    "total_score": record.total_score
                }
                for record in decks_attempted
            ]
        }  # TODO check if this is the best way to send the data back

# properly revieww the code below on 26-11-2021


class StudyCard(Resource):

    def get(self, user_id, api_key, deck_id, card_id):
        if not checkUserValid(user_id=user_id, api_key=api_key):
            invalidUserCred()

        card = Card.query.filter((Card.deck_id == deck_id) & (
            Card.card_id > card_id)).first()

        if card is None:
            # either the deck is finished or in id sent is not valid
            return {'card_id': -1}  # TODO send back proper response

        # TODO check if this is the best way to send the data back
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
            # first card solved, thus making a solve_id
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
