import api.v1.pigment_routes
import api.v1.mix_routes
import api.v1.munsell
from api import app
from api.routing import route_for
from flask import request


@app.route("/v1/", methods=['GET'])
def v1_api_routes():
    """
    A pigment and palette API. Version 1.
    """
    if request.method == 'GET':
        return {
            'pigments': route_for('pigments'),
            'mixes': route_for('mixes'),
            'munsell': route_for('munsell_routes'),
        }
