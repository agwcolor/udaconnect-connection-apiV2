from flask import Flask, jsonify, request, g, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from . import grpc_server

db = SQLAlchemy()


def create_app(env=None):
    #grpc_server.serve()
    from app.config import config_by_name

    app = Flask(__name__)
    with app.app_context():

        app.config.from_object(config_by_name[env or "test"])

        CORS(app)  # Set CORS for development
        db.init_app(app)

        @app.route("/health")
        def health():
            return jsonify("healthy")
        grpc_server.serve()

        return app
