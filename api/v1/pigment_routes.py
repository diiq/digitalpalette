from api import app
from flask import request
from flask_api import FlaskAPI, status, exceptions
from api.models import Pigment


@app.route("/v1/pigments", methods=['GET'])
def pigments():
    """
    List pigments.
    """
    if request.method == 'GET':
        return [p.short_dict() for p in Pigment.query.all()]


@app.route("/v1/pigment/<int:pigment_id>", methods=['GET'])
def pigment(pigment_id):
    """
    Get full specs on a pigment.
    """
    if request.method == 'GET':
        return Pigment.query.get(pigment_id).full_dict()
