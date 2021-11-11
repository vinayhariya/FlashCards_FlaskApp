from flask import current_app as app  # for the correct Flask App context


@app.route("/")
def index():
    return "hello world"
