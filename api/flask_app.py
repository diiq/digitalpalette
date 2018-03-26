from flask_api import FlaskAPI
from flask_cors import CORS, cross_origin
from config import config
import os

flask_app = FlaskAPI(__name__)
CORS(flask_app)

flask_app.config.update(
    DEBUG=True,
    SQLALCHEMY_DATABASE_URI=config.database_connection_string(),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
