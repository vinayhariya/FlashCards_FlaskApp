from flask_restful import reqparse

login_user_parser = reqparse.RequestParser()
login_user_parser.add_argument("username")
login_user_parser.add_argument("password")

register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument("username")
register_user_parser.add_argument("email")
register_user_parser.add_argument("password")


deck_creation_parser = reqparse.RequestParser()
deck_creation_parser.add_argument("user_id", type=int)
deck_creation_parser.add_argument("api_key")
deck_creation_parser.add_argument("deckname")
deck_creation_parser.add_argument("public")

deck_updation_parser = reqparse.RequestParser()
deck_updation_parser.add_argument("user_id", type=int)
deck_updation_parser.add_argument("api_key")
deck_updation_parser.add_argument("deckname")
deck_updation_parser.add_argument("public")
deck_updation_parser.add_argument("deck_id", type=int)

card_creation_parser = reqparse.RequestParser()
card_creation_parser.add_argument("user_id", type=int)
card_creation_parser.add_argument("api_key")
card_creation_parser.add_argument("deck_id", type=int)
card_creation_parser.add_argument("front")
card_creation_parser.add_argument("back")

card_updation_parser = reqparse.RequestParser()
card_updation_parser.add_argument("user_id", type=int)
card_updation_parser.add_argument("api_key")
card_updation_parser.add_argument("deck_id", type=int)
card_updation_parser.add_argument("card_id", type=int)
card_updation_parser.add_argument("front")
card_updation_parser.add_argument("back")

solving_deck_parser = reqparse.RequestParser()
solving_deck_parser.add_argument("user_id", type=int)
solving_deck_parser.add_argument("api_key")
solving_deck_parser.add_argument("deck_id", type=int)
solving_deck_parser.add_argument("card_id", type=int)
solving_deck_parser.add_argument("solve_id", type=int)
solving_deck_parser.add_argument("feedback")