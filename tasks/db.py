from fabric.api import local, settings, task
from config import config


@task
def new():
    """Creates an empty, tableless database"""
    local("createdb %s" % config.database_name())


@task
def create():
    """Creates a new db and builds tables (short-circuiting migrations)"""
    from api.db import db

    new()
    db.create_all()
    local("alembic -c%s stamp head" % config.alembic_ini())


@task
def seed():
    """Inserts seed data into the db for testing and development purposes"""
    print("OK! I did nothing.")


@task
def drop():
    """Drops database named in .env"""
    local("dropdb %s" % config.database_name())


@task
def reset():
    """Drops, creates, and seeds a new DB"""
    with settings(warn_only=True):
        drop()
    create()
    seed()


@task
def setup():
    """Takes an existing DB and reforms/reseeds it.

    Better than reset for use with EB instances, or when the db is
    being accessed.

    """
    from api.db import db
    conn = db.engine.connect()
    conn.execute("commit;")
    conn.execute("drop schema public cascade;")
    conn.execute("create schema public;")
    db.session.rollback()
    db.create_all()

    seed()
