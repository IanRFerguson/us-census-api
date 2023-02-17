#!/bin/python3
from flask import Flask
import os
import logging
from dotenv import load_dotenv

here = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO)
load_dotenv(os.path.join(here, ".env"))

##########


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY")

    from census_app.routes import bp as route_tree

    app.register_blueprint(route_tree)

    logging.info(" === APP RUNNING ===")

    return app
