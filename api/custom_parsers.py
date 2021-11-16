from flask_restful import reqparse

login_user_parser = reqparse.RequestParser()
login_user_parser.add_argument("username")
login_user_parser.add_argument("password")

register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument("username")
register_user_parser.add_argument("email")
register_user_parser.add_argument("password")


deck_creation_parser = reqparse.RequestParser()
deck_creation_parser.add_argument("user_id")
deck_creation_parser.add_argument("api_key")
deck_creation_parser.add_argument("deckname")
deck_creation_parser.add_argument("public")

card_creation_parser = reqparse.RequestParser()
card_creation_parser.add_argument("user_id")
card_creation_parser.add_argument("api_key")
card_creation_parser.add_argument("deck_id")
card_creation_parser.add_argument("card_id")
card_creation_parser.add_argument("front")
card_creation_parser.add_argument("back")
