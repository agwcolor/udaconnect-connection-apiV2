from flask import Flask, jsonify, request, g, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import grpc
import logging
from concurrent import futures
import app.connection_pb2
import app.connection_pb2_grpc
from app.controllers import ConnectionDataResource
import app.grpc_server as grpc_server
from grpc_reflection.v1alpha import reflection
# from common import db
# import config

# db = SQLAlchemy()


def create_app(env=None):
    from app.config import config_by_name
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[env or "test"])

    CORS(app)  # Set CORS for development

    from app.common import db
    db.init_app(app)

    @app.route("/health")
    def health():
        return jsonify("healthy")

    return app

app = create_app()
'''
with app.app_context():
        grpc_server.serve()
'''
'''
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5002")
'''
