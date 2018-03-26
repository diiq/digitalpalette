import os


class Config(object):
    # TODO memoize these?

    def project_root(self):
        return os.path.abspath(os.path.dirname(__file__))

    def root_url(self):
        return os.environ.get('ROOT_URL')

    def database_connection_string(self):
        if os.environ.get('DATABASE_URL'):
            return os.environ['DATABASE_URL']
        return "postgresql://%s:%s@%s:%s/%s" % (
            os.environ.get('DATABASE_USER'),
            os.environ.get('DATABASE_PASSWORD'),
            os.environ.get('DATABASE_HOST'),
            os.environ.get('DATABASE_PORT'),
            self.database_name()
        )

    def database_name(self):
        return os.environ.get('DATABASE_NAME')

    def debug(self):
        return os.environ.get('FLASK_DEBUG')

    def alembic_ini(self):
        return "%s/alembic/alembic.ini" % self.project_root()

    def allowed_origins(self):
        return map(lambda x: x.strip(),
                   os.environ.get('ALLOWED_ORIGINS').split(','))


config = Config()
