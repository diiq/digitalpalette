from api import app
from flask import request, abort
from flask_api import FlaskAPI, status, exceptions
from lib.munsell import color_from_name, numerical_ladder, mix_ladder, rainbow, page
from lib.color import Mix


def color(key="color"):
    name = request.args.get(key)
    if not name:
        abort(422, "You must specify a `{0}`".format(key))
    return color_from_name(name)

@app.route("/v1/munsell/color", methods=['GET'])
def plain_color():
    """Fetch a color by its munsell designation.

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
        return color().stats_dict()


@app.route("/v1/munsell/color/sunlight", methods=['GET'])
def sunlight():
    """A color hightened in value and warmth, as if in sunlight.

    """
    if request.method == 'GET':
        return color().in_sunlight().stats_dict()


@app.route("/v1/munsell/color/shadow", methods=['GET'])
def shadow():
    """A color lowered in value and warmth, as if in shadow.

    """
    if request.method == 'GET':
        return color().in_shadow().stats_dict()


@app.route("/v1/munsell/color/complement", methods=['GET'])
def complement():
    """The equal-chroma (or as close as possible) complement of a color.

    A munsell-complement will mix to *very close to gray*, but a
    perfect grey mix is not guaranteed, nor is a 50/50 mix necessarily
    the right blend to get there; the colors are guaranteed to be the
    same value.

    """
    if request.method == 'GET':
        return color().complement().stats_dict()


@app.route("/v1/munsell/ladder", methods=['GET'])
def ladder():
    """An equally-spaced ladder of `steps` colors from `start_color` to
    `end_color`. The default is a ladder through Munsell-space; you
    can also specify the "mix" `method` to create a paint-mixing
    ladder.

    """
    if request.method == 'GET':
        a = color("start_color")
        b = color("end_color")
        steps = int(request.args.get("steps"))
        if not request.args.get("method") or request.args.get("method") == "munsell":
            return [x.stats_dict() for x in numerical_ladder(a, b, steps)]
        elif request.args.get("method") == "mix":
            return [x.stats_dict() for x in mix_ladder(a, b, steps)]


@app.route("/v1/munsell/mix", methods=['GET'])
def munsell_mix():
    """A paint-mixed in-between color, mixed from `a_color` and `b_color`
    in proportion based on `a_parts` and `b_parts`.

    The default is an even 50/50 mix.

    """
    if request.method == 'GET':
        a = color("a_color")
        b = color("b_color")
        a_prop = float(request.args.get("a_parts") or 1)
        b_prop = float(request.args.get("b_parts") or 1)
        return Mix([a.p(a_prop), b.p(b_prop)]).stats_dict()


@app.route("/v1/munsell/rainbow", methods=['GET'])
def munsell_rainbow():
    """A rainbow is an even sampling of hues at a single value and chroma.

    Takes `value`, `chroma`, `steps` and an optional `offset`, which sets the starting hue.

    """
    if request.method == 'GET':
        value = float(request.args.get("value"))
        chroma = float(request.args.get("chroma"))
        steps = int(request.args.get("steps") or 10)
        offset = float(request.args.get("offset") or 0)

        if not value or not chroma:
            abort(422, "You must specify a value and a chroma")
        return [x.stats_dict() for x in rainbow(value, chroma, steps, offset)]


@app.route("/v1/munsell/page", methods=['GET'])
def munsell_page():
    """A page is an even sampling of across value and chroma for a given `hue`.
    Optionally takes `value_steps` and `chroma_steps`, each fo which default to 0.

    """
    if request.method == 'GET':
        hue = request.args.get("hue")
        chroma_steps = int(request.args.get("chroma_steps") or 10)
        value_steps = int(request.args.get("value_steps") or 10)

        if not hue:
            abort(422, "You must specify a hue")

        this_page = page(hue, value_steps, chroma_steps)

        return [[x.stats_dict() for x in ladder] for ladder in this_page]
