import api.v1.munsell.color_routes
from api import app
from api.routing import route_for
from flask import request


@app.route("/v1/munsell/", methods=['GET'])
def munsell_routes():
    """An API for Munsell-system color manipulation.

    Munsell colors are specified as "Hue Value/Chroma" where chroma
    ranges between 0 and 14, hue between 0 and 10 (but more typically
    between 1 and 9) and hue is a number between 0 and 10 followed by
    one of 'R', 'YR', 'Y', 'GY', 'G', 'BG', 'B', 'PB', 'P', or 'RP'

    Some sample colors:
    "5.0R 3/7" -- a dark, medium-dull red.
    "7.0PB 6/14" -- a brilliant royal blue.
    "7.0GY 8/10" -- a bright grassy green.
    "7.0GY 8/0" -- a pure light grey (0 chroma means no green-yellow).

    Some colors don't actually exist -- a color cannot be very
    high-chroma and very low value. The API will sacrifice chroma to
    achieve the requested value.

    Some colors cannot be represented on a screen, or in the sRGB
    space. These colors will be clipped to fit in the available gamut.

    """
    if request.method == 'GET':
        return {
            'color': route_for('plain_color', color="5.0R 3/7"),
            'complement': route_for('complement', color="5.0R 3/7"),
            'sunlight': route_for('sunlight', color="5.0R 3/7"),
            'shadow': route_for('shadow', color="5.0R 3/7"),
            'ladder': route_for('ladder', start_color="5.0R 3/7", end_color="7.0GY 8/10", steps=5),
            'mix': route_for('munsell_mix', a_color="5.0R 3/7", b_color="7.0GY 8/10"),
        }
