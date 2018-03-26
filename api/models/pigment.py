from api.db import db, Model
from lib.color import Color
from api.routing import route_for


class Pigment(Model, db.Model):
    __tablename__ = 'pigments'

    id = db.Column(db.Integer,
                   db.Sequence('pigments_id_seq'),
                   primary_key=True)
    spectrum = db.Column(db.ARRAY(db.Float))
    name = db.Column(db.String)

    def color(self):
        return Color(self.spectrum, 1, self.name)

    def short_dict(self):
        return {
            'id': self.id,
            'rgb': self.color().to_rgb().tolist(),
            'name': self.name,
            'url': route_for('pigment', pigment_id=self.id)
        }

    def full_dict(self):
        return {
            'id': self.id,
            'rgb': self.color().to_rgb().tolist(),
            'name': self.name,
            'spectrum': self.spectrum,
            'url': route_for('pigment', pigment_id=self.id)
        }


class PigmentQuery(db.Query):
    pass


Pigment.query_class = PigmentQuery
