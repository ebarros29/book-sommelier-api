import os

from flask import Flask

from api.extensions import db
from api.routes.book_routes import book_bp
from api.routes.docs import docs_bp


def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not defined")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(book_bp)
    app.register_blueprint(docs_bp)

    return app


app = create_app()
