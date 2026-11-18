import os

from flask import Flask, jsonify, render_template, request, session

from config import Config
from database.db import close_db
from routes.auth import auth_bp
from routes.listings import listings_bp
from routes.messages import messages_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.teardown_appcontext(close_db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(messages_bp)

    @app.context_processor
    def inject_globals():
        return {
            "current_user": session.get("user_name"),
            "hostels": Config.HOSTELS,
            "categories": Config.CATEGORIES,
            "conditions": Config.CONDITIONS,
        }

    @app.errorhandler(413)
    def too_large(_e):
        return jsonify(error="Image is too large (max 5 MB)."), 413

    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found."), 404
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
