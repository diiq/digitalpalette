from api import app
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

print("here!")

@app.route("/v1/pigments", methods=['GET'])
def notes_list():
    """
    List pigments.
    """
    if request.method == 'GET':
        return {'message': "Hello!"}
