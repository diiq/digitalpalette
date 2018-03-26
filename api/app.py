from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from config import config
import os

app = FlaskAPI(__name__)
CORS(app)

app.config.update(
    DEBUG=True,
    SQLALCHEMY_DATABASE_URI=config.database_connection_string(),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)
