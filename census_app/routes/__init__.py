from flask import Blueprint

bp = Blueprint("routes", __name__)

from census_app.routes import routes
