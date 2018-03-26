from flask_api import FlaskAPI
from flask_cors import CORS, cross_origin
from config import config
import os
from flask import Blueprint

theme = Blueprint(
    'api',
    __name__,
    url_prefix='/browsable-api',
    template_folder='templates',
    static_folder='static'
)

flask_app = FlaskAPI(__name__)
CORS(flask_app)

flask_app.config.update(
    DEBUG=True,
    SQLALCHEMY_DATABASE_URI=config.database_connection_string(),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)


flask_app.register_blueprint(theme)
#print(flask_app.blueprints['flask-api'].static_folder)
