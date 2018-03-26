from api import app
from flask import request
from flask_api import FlaskAPI, status, exceptions
from api.models import Pigment

from lib.color import Mix


@app.route("/v1/mixes", methods=['GET', 'POST'])
def mixes():
    """
    POST to mix a set of pigments. For instance, try making a nice purple by mixing titanium white, ultramarine blue, and cadmium red:

    <code>{
      "pigments": [{
        "id": 2,
        "proportion": 2
      },
      {
        "id": 16,
        "proportion": 1
      },
      {
        "id": 45,
        "proportion": 2
      }]
    }</code>

    """
    if request.method == 'POST':
        data = request.data
        pigments = data['pigments']
        colors = [Pigment.query.get(p['id']).color().p(p['proportion']) for p in pigments]
        mix = Mix(colors).to_color()
        return {
            'pigments': pigments,
            'rgb': mix.to_rgb().tolist(),
            'hex': mix.to_hex(),
            'spectrum': mix.spectrum.tolist(),
            'name': mix.name
        }

    if request.method == 'GET':
        return {'message': "Try POSTing."}, status.HTTP_204_NO_CONTENT
