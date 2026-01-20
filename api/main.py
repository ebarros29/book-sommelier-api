import os

from flask import Flask

from api.extensions import db
from api.routes.auth_routes import auth_bp
from api.routes.book_routes import book_bp
from api.routes.docs import docs_bp
from api.routes.insights import api_bp as insights_bp


def create_app():
    app = Flask(__name__)

    # Database config
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not defined. Using temp SQLite instead.")
        database_url = "sqlite:///temp.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT config (can be overridden via env)
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-jwt-secret")
    )
    app.config["JWT_ACCESS_EXPIRES"] = int(os.getenv("JWT_ACCESS_EXPIRES", "900"))
    app.config["JWT_REFRESH_EXPIRES"] = int(os.getenv("JWT_REFRESH_EXPIRES", "86400"))

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(book_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(insights_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
