from api.db import db, Model


class Pigment(Model, db.Model):
    __tablename__ = 'pigments'

    id = db.Column(db.Integer,
                   db.Sequence('pigments_id_seq'),
                   primary_key=True)


class PigmentQuery(db.Query):
    pass


Pigment.query_class = PigmentQuery
