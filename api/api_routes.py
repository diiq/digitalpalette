from api import app
from api.routing import route_for
from flask import request


@app.route("/", methods=['GET'])
def api_routes():
    """
    A pigment and palette API.
    """
    if request.method == 'GET':
        return {
            'pigments': route_for('pigments'),
            'mixes': route_for('mixes'),
        }
