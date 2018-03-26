from fabric.api import task, local
from config import config


@task
def run():
    """Migrates database to current head"""
    local("alembic -c%s upgrade head" % config.alembic_ini())


@task
def new(message=None):
    """:message - Creates new, empty migration. Consider autogen."""
    if not message:
        raise TypeError("""
        You must supply a message, e.g.:
        $ fab migration.new:"I'm a little teapot"
        """)
    local("alembic -c%s revision -m \"%s\"" % (config.alembic_ini(), message))


@task
def autogen(message):
    """:message - Creates new migration based on current models."""
    if not message:
        raise TypeError("""
        You must supply a message, e.g.:
        $ fab migration.autogen:"I'm a little teapot"
        """)
    local("alembic -c%s revision --autogenerate -m \"%s\"" %
          (config.alembic_ini(), message))
