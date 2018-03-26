import lib.paints as paints
from api.db import db
from api.models import Pigment

def seed():
    seed_pigments()

def seed_pigments():
    for c in paints.color_names:
        color = getattr(paints, c)
        pig = Pigment()
        pig.name = color.name
        pig.spectrum = color.spectrum
        db.session.add(pig)
