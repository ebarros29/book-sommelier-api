import os
from flask import Flask
from api.extensions import db
from api.routes.book_routes import book_bp
from api.routes.docs import docs_bp

from api.routes.insights import api_bp as insights_bp 

def create_app():
    app = Flask(__name__)

 
    database_url = os.getenv("DATABASE_URL")
    

    if not database_url:
        print("DATABASE_URL not defined. Using temp SQLite instead.")
        database_url = "sqlite:///temp.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

 
    app.register_blueprint(book_bp)
    app.register_blueprint(docs_bp)

    app.register_blueprint(insights_bp) 

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
