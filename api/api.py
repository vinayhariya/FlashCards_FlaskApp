from flask_restful import Resource
from api.models import Card, Deck, Feedback, PerCard, SolvingDeck, User
from api.database import db
from api.validation import DoesNotExistError, LoginError, NotAllowedError, UnauthenticatedUserError
from api.custom_parsers import login_user_parser, register_user_parser, deck_creation_parser, deck_updation_parser, card_creation_parser, card_updation_parser, solving_deck_parser
from api.custom_check_functions import check_username, check_password, check_email, checkUserValid
import secrets
from datetime import datetime
from sqlalchemy import desc


class UserLoginAPI(Resource):
    """
    For Login
    """

    def get(self, user_id):
        """To get the credentials of the user requested

        Args:
            user_id (int): id of the user (used in the database)

        Raises:
            DoesNotExistError: User id does not exist

        Returns:
            json response
        """
        user = User.query.filter(User.user_id == user_id).first()

        if user is None:
            raise DoesNotExistError(
                error_message=f"User with user_id = {user_id} does not exist.")

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
        }, 200

    def post(self):
        """To securly check the credentials of the user

        Raises:
            LoginError

        Returns:
            json response
        """
        args = login_user_parser.parse_args()
        username = check_username(args["username"])
        password = check_password(args["password"])

        user = User.query.filter(
            (User.username == username) & (User.password == password)
        ).first()

        if user:
            return {
                "status_code": 200,
                "logged_in": True,
                "api_key": user.api_key
            }, 200
        else:
            raise LoginError(error_message="Invalid login details !")


class UserRegisterAPI(Resource):
    """
    For Register
    """

    def post(self):
        """Creating a new user

        Raises:
            NotAllowedError

        Returns:
            json response
        """
        args = register_user_parser.parse_args()
        username = check_username(args["username"])
        password = check_password(args["password"])
        email = check_email(args["email"])

        user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if user:
            if User.query.filter(User.email == email).first():
                raise NotAllowedError(
                    error_message="Email is taken. Use another email.")
            else:
                raise NotAllowedError(
                    error_message="Username is taken. Use another username.")

        api_key = secrets.token_urlsafe(16)

        while User.query.filter(User.api_key == api_key).first():
            api_key = secrets.token_urlsafe(16)

        new_user = User(
            username=username, email=email, password=password, api_key=api_key
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            "status_code": 201,
            "message": "User registered successfully"
        }, 201


class UserDeckList(Resource):
    """
    For getting the list of decks created by the user
    """

    def get(self, user_id, api_key):
        """Used to get the list of decks created by the user

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made

        Raises:
            UnauthenticatedUserError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

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
            "status_code": 200,
            "user_id": user_id,
            "no_of_decks": user.no_of_decks(),
            "decks": deck_list
        }, 200


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

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & ((Deck.author_id == user_id) | (Deck.public == True))).first()

        if deck is None:
            if Deck.query.filter(Deck.deck_id).first():
                raise NotAllowedError(
                    error_message='Deck does not exist for this user.')
            else:
                raise DoesNotExistError(error_message='Deck does not exist.')

        creator = deck.author_id == user_id

        return {
            'status_code': 200,
            'creator': creator,
            'deck_id': deck.deck_id,
            'deck_author': deck.author.username,
            'deck_name': deck.deckname,
            'public': deck.public,
            'no_of_cards': deck.no_of_cards()
        }, 200

    def post(self):
        """Used to enter into of a new deck into the database (CREATE) 

        Raises:
            UnauthenticatedUserError,
            NotAllowedError

        Returns:
            json response
        """
        args = deck_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deckname = args["deckname"]
        public = args["public"]

        if isinstance(deckname, str):
            deckname = deckname.strip()

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        if not deckname:
            raise NotAllowedError(error_message="Deckname should not be empty")

        deck_present = Deck.query.filter(
            (Deck.author_id == user_id) & (Deck.deckname == deckname)).first()

        if deck_present:
            raise NotAllowedError(
                error_message='Deck with same name is already present.')
        else:
            new_deck = Deck(author_id=user_id,
                            deckname=deckname, public=bool(public))
            db.session.add(new_deck)
            db.session.commit()

        return {
            "status_code": 201,
            "message": "Deck created successfully"
        }, 201

    def put(self):
        """Used for updating the information of the exisiting deck (UPDATE)

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """
        args = deck_updation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        deckname = args["deckname"]
        public = args["public"]

        if isinstance(deckname, str):
            deckname = deckname.strip()

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        u_deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & (Deck.author_id == user_id)).first()

        if not u_deck:  # deck does not exist
            raise DoesNotExistError(error_message='Deck does not exist.')

        if deckname:

            duplicate_deck_name = Deck.query.filter((Deck.deck_id != deck_id) & (
                Deck.author_id == user_id) & (Deck.deckname == deckname)).first()

            if duplicate_deck_name:  # if a deck with that name already exists
                raise NotAllowedError(
                    error_message='Deck with same name is already present.')

            u_deck.deckname = deckname

        u_deck.public = bool(public)

        db.session.add(u_deck)
        db.session.commit()

        return {
            "status_code": 201,
            "message": "Deck updated successfully"
        }, 201

    def delete(self, user_id, api_key, deck_id):
        """Used to delete the specific deck requested (DELETE)

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """
        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        deck_exists = Deck.query.filter(
            (Deck.author_id == user_id) & (Deck.deck_id == deck_id)).first()

        if deck_exists is None:
            if Deck.query.filter(Deck.deck_id).first():
                raise NotAllowedError(
                    error_message='Deck does not exist for this user.')
            else:
                raise DoesNotExistError(error_message='Deck does not exist.')

        db.session.delete(deck_exists)
        db.session.commit()

        return {
            "status_code": 200,
            "message": "Deck deleted successfully"
        }, 200


class DeckCardList(Resource):

    def get(self, user_id, api_key, deck_id):
        """Used to get the list of cards of a particular deck

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        deck = Deck.query.filter(
            (Deck.deck_id == deck_id) & ((Deck.author_id == user_id) | (Deck.public == True))).first()

        if deck is None:
            if Deck.query.filter(Deck.deck_id).first():
                raise NotAllowedError(
                    error_message='Deck does not exist for this user.')
            else:
                raise DoesNotExistError(error_message='Deck does not exist.')

        card_list = [
            {'card_id': card.card_id,
             'front': card.front,
             'back': card.back
             }
            for card in deck.cards
        ]

        return {
            "status_code": 200,
            'creator': deck.author_id == user_id,
            'deck_id': deck.deck_id,
            'deck_name': deck.deckname,
            'public': deck.public,
            'no_of_cards': deck.no_of_cards(),
            "cards": card_list
        }, 200


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

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        card = Card.query.filter(Card.card_id == card_id).first()

        if not card:
            raise DoesNotExistError(error_message='Card does not exist.')

        if not card.deck.public:
            if not (card.deck.author_id == user_id):
                raise NotAllowedError(
                    error_message='Card does not exist for this user.')

        return{
            "status_code": 200,
            'creator': card.deck.author_id == user_id,
            'deck_id': card.deck.deck_id,
            'deck_name': card.deck.deckname,
            'card_id': card.card_id,
            'card_front': card.front,
            'card_back': card.back
        }, 200

    def post(self):
        """Used to create a new card to be part of a deck created by user (CREATE)

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """
        args = card_creation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        front = args["front"]
        back = args["back"]

        if isinstance(front, str):
            front = front.strip()

        if isinstance(back, str):
            back = back.strip()

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        deck = Deck.query.filter((Deck.deck_id == deck_id) & (
            Deck.author_id == user_id)).first()

        if deck is None:
            if Deck.query.filter(Deck.deck_id).first():
                raise NotAllowedError(
                    error_message='Deck does not exist for this user.')
            else:
                raise DoesNotExistError(error_message='Deck does not exist.')

        if not front:
            raise NotAllowedError(
                error_message='Front cannot be empty.')

        if not back:
            raise NotAllowedError(
                error_message='Back cannot be empty.')

        card = Card.query.filter((Card.deck_id == deck_id) & (
            (Card.front == front))).first()

        if card:
            raise NotAllowedError(
                error_message='Card with same details is already present.')

        new_card = Card(front=front, back=back, deck_id=deck_id)

        db.session.add(new_card)
        db.session.commit()

        return {
            "status_code": 201,
            "message": "Card added successfully"
        }, 201

    def put(self):
        """Used to update a particular card of a deck (UPDATE)

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """
        args = card_updation_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        card_id = args["card_id"]
        front = args["front"]
        back = args["back"]

        if isinstance(front, str):
            front = front.strip()

        if isinstance(back, str):
            back = back.strip()

        print(f'Front{front}, Back{back}.')

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        card = Card.query.filter(
            (Card.deck_id == deck_id) & (Card.card_id == card_id)).first()

        if card is None:
            raise DoesNotExistError(error_message='Card does not exist.')

        if not (card.deck.author_id == user_id):
            raise NotAllowedError(
                error_message='Card does not exist for this user.')

        if front:
            c = Card.query.filter((Card.card_id != card_id) & (Card.deck_id == deck_id)
                                  & (Card.front == front)).first()
            if c:
                raise NotAllowedError(
                    error_message='Card front with same details is already present.')

            card.front = front

        if back:
            card.back = back

        db.session.add(card)
        db.session.commit()

        return {
            "status_code": 201,
            "message": "Card updated successfully"
        }, 201

    def delete(self, user_id, api_key, deck_id, card_id):
        """Used to delete a particular card from a deck (DELETE)

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested
            card_id (int): id of the specific card requested

        Raises:
            UnauthenticatedUserError,
            NotAllowedError,
            DoesNotExistError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        c = Card.query.filter((Card.card_id == card_id) &
                              (Card.deck_id == deck_id)).first()

        if c is None:
            raise DoesNotExistError(error_message='Card does not exist.')

        if not (c.deck.author_id == user_id):
            raise NotAllowedError(
                error_message='Card does not exist for this user.')

        db.session.delete(c)
        db.session.commit()

        return {
            "status_code": 200,
            "message": "Card deleted successfully"
        }, 200


class PublicDecks(Resource):
    def get(self, user_id, api_key):
        """To get all the public decks available

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made

        Raises:
            UnauthenticatedUserError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

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

        return {
            "status_code": 200,
            "no_of_decks": len(deck_list),
            "decks": deck_list
        }, 200


class UserDeckScore(Resource):

    def get(self, user_id, api_key, deck_id):
        """To get all the scores made by the user of a specific deck in order of the latest attempt

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested

        Raises:
            UnauthenticatedUserError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        times_solved = SolvingDeck.query.filter((SolvingDeck.user_id == user_id) & (
            SolvingDeck.deck_id == deck_id)).order_by(desc(SolvingDeck.start_time)).all()

        return {
            'status_code': 200,
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
        }, 200


class UserDeckAttempted(Resource):

    def get(self, user_id, api_key):
        """To get all the decks attempted by the user order of the latest attempt

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made

        Raises:
            UnauthenticatedUserError

        Returns:
            json response
        """

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        decks_attempted = SolvingDeck.query.filter(
            SolvingDeck.user_id == user_id).order_by(desc(SolvingDeck.start_time)).all()

        return {
            'status_code': 200,
            'user_id': user_id,
            'decks_attempted': [
                {
                    'creator': record.solvedecks_r.author_id == user_id,
                    'deck_id': record.solvedecks_r.deck_id,
                    'public': record.solvedecks_r.public,
                    'deckname': record.solvedecks_r.deckname,
                    'date': record.start_time.strftime("%d-%b-%Y"),
                    'author': record.solvedecks_r.author.username,
                    'total_score': record.total_score
                }
                for record in decks_attempted
            ]
        }, 200


class StudyCard(Resource):

    def get(self, user_id, api_key, deck_id, card_id):
        """To get a single card in study mode

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            deck_id (int): id of the specific deck requested
            card_id (int): id of the specific card requested

        Raises:
            UnauthenticatedUserError,
            NotAllowedError

        Returns:
            json response
        """
        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        card = Card.query.filter((Card.deck_id == deck_id) & (
            Card.card_id > card_id)).first()

        if card is None:
            raise NotAllowedError(error_message="Error in Studying Card")

        return {
            "status_code": 200,
            "card": {
                'card_id': card.card_id,
            },
            'front': card.front,
            'back': card.back,
            'message': 'Finished Deck, Score updated in the table'
        }, 200

    def post(self):
        """Add the feedback of a single card studied by the user

        Raises:
            UnauthenticatedUserError

        Returns:
            json response
        """
        args = solving_deck_parser.parse_args()

        user_id = args["user_id"]
        api_key = args["api_key"]
        deck_id = args["deck_id"]
        card_id = args["card_id"]
        solve_id = args["solve_id"]
        feedback = args["feedback"]

        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

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
            return {
                "status_code": 200,
                "card": {
                    'card_id': -1,
                },
                'message': 'Finished Deck, Score updated in the table'
            }, 200

        return {
            "status_code": 200,
            "solve_id": solve_id,
            "card": {
                'card_id': card.card_id,
                'front': card.front,
                'back': card.back
            }
        }, 200


class PublicDeckAuthorRelated(Resource):
    def get(self, user_id, api_key, author_name):
        """To get all the public decks affiliated with the particular author

        Args:
            user_id (int): id of the user (used in the database)
            api_key (string - 16 chars): used for user api auth everytime a request is made
            author_name ([type]): name of the author/creator of the deck

        Raises:
            UnauthenticatedUserError

        Returns:
            json response
        """
        if not checkUserValid(user_id=user_id, api_key=api_key):
            raise UnauthenticatedUserError(
                error_message="Invalid API User Credentials")

        author = User.query.filter(User.username == author_name).first()

        decks = Deck.query.filter(
            (Deck.author_id == author.user_id) & (Deck.public == True)).all()

        deck_list = [
            {
                'deck_id': deck.deck_id,
                'deck_name': deck.deckname,
                'public': deck.public,
                'no_of_cards': deck.no_of_cards(),
            }
            for deck in decks
        ]

        return {
            "status_code": 200,
            "no_of_decks": len(deck_list),
            "decks": deck_list,
            "author": author_name
        }, 200
