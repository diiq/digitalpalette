from flask_sqlalchemy import SQLAlchemy
import pprint

from api.flask_app import flask_app

db = SQLAlchemy(flask_app)


class Model(object):
    @classmethod
    def reset_id_counter(cls):
        if hasattr(cls, 'id'):
            sql = "SELECT setval('%s_id_seq', max(id)+1) FROM %s;"
            db.engine.execute(sql % (cls.__tablename__, cls.__tablename__))

    def __repr__(self):
        if hasattr(self, 'repr_attributes'):
            attributes = self.repr_attributes
        elif hasattr(self, 'id'):
            attributes = ['id']

        attrlist = [u"{}={}".format(attr, getattr(self, attr).__repr__())
                    for attr in attributes]
        attrlist = u", ".join(attrlist)
        return u"<{}({})>".format(self.__class__.__name__, attrlist)

    def __str__(self):
        if hasattr(self, 'str_attributes'):
            attributes = self.str_attributes
        elif hasattr(self, 'public_attributes'):
            attributes = self.public_attributes
        else:
            attributes = [k for k in self.__dict__.keys()
                          if not k.startswith(u'_')]

        attrdict = {attr: getattr(self, attr) for attr in attributes}

        return u"{}:\n{}".format(
            self.__class__.__name__,
            pprint.pformat(attrdict))

    def public_dict(self):
        return {attr: getattr(self, attr) for attr in self.public_attributes}
